"""
Job alerting system.
"""
from typing import List
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from ..models import Job
from ..utils import get_config

logger = logging.getLogger(__name__)


class ConsoleAlerter:
    """Console-based job alerts."""
    
    def __init__(self):
        """Initialize console alerter."""
        self.config = get_config()
        self.min_score = self.config.get('alerts.triggers.min_relevance_score', 75)
    
    def send_alerts(self, jobs: List[Job]):
        """
        Send console alerts for jobs.
        
        Args:
            jobs: List of jobs to alert about
        """
        if not jobs:
            logger.info("No jobs to alert about")
            return
        
        # Filter jobs that meet alert criteria
        alert_jobs = [job for job in jobs if job.relevance_score >= self.min_score]
        
        if not alert_jobs:
            logger.info(f"No jobs with relevance score >= {self.min_score}")
            return
        
        print("\n" + "="*80)
        print(f"🔔 NEW JOB ALERTS ({len(alert_jobs)} opportunities)")
        print("="*80)
        
        for job in alert_jobs:
            self._print_job_alert(job)
        
        print("="*80 + "\n")
    
    def _print_job_alert(self, job: Job):
        """Print single job alert."""
        print(f"\n📌 {job.title}")
        print(f"   Company: {job.company}")
        
        if job.remote_type:
            print(f"   Location: {job.remote_type.value}")
        elif job.locations:
            print(f"   Location: {', '.join(job.locations)}")
        
        if job.stipend_salary:
            print(f"   💰 {job.stipend_salary}")
        
        print(f"   ⭐ Relevance: {job.relevance_score:.1f}/100")
        print(f"   🎯 Skill Match: {job.skill_match_score:.1f}/100")
        
        if job.required_skills:
            print(f"   Skills: {', '.join(job.required_skills[:5])}")
        
        print(f"   🔗 Apply: {job.url}")


class EmailAlerter:
    """Email-based job alerts."""
    
    def __init__(self):
        """Initialize email alerter."""
        self.config = get_config()
        self.enabled = self.config.get('alerts.email_enabled', False)
        
        if self.enabled:
            self.smtp_server = self.config.get('alerts.email.smtp_server')
            self.smtp_port = self.config.get('alerts.email.smtp_port', 587)
            self.sender = self.config.get('alerts.email.sender_email')
            self.password = self.config.get('alerts.email.sender_password')
            self.recipient = self.config.get('alerts.email.recipient_email')
    
    def send_alerts(self, jobs: List[Job]):
        """
        Send email alerts for jobs.
        
        Args:
            jobs: List of jobs to alert about
        """
        if not self.enabled:
            logger.debug("Email alerts disabled")
            return
        
        if not jobs:
            logger.info("No jobs to email about")
            return
        
        try:
            # Create email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🔔 {len(jobs)} New Job Opportunities"
            msg['From'] = self.sender
            msg['To'] = self.recipient
            
            # Create HTML content
            html_content = self._create_email_html(jobs)
            msg.attach(MIMEText(html_content, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender, self.password)
                server.send_message(msg)
            
            logger.info(f"Sent email alert for {len(jobs)} jobs to {self.recipient}")
        except Exception as e:
            logger.error(f"Error sending email alert: {e}")
    
    def _create_email_html(self, jobs: List[Job]) -> str:
        """Create HTML email content."""
        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                .job { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
                .title { font-size: 18px; font-weight: bold; color: #333; }
                .company { color: #666; margin: 5px 0; }
                .detail { margin: 3px 0; }
                .link { display: inline-block; margin-top: 10px; padding: 8px 15px; 
                        background: #007bff; color: white; text-decoration: none; border-radius: 3px; }
            </style>
        </head>
        <body>
            <h2>🔔 New Job Opportunities</h2>
        """
        
        for job in jobs:
            html += f"""
            <div class="job">
                <div class="title">{job.title}</div>
                <div class="company">{job.company}</div>
                <div class="detail">⭐ Relevance: {job.relevance_score:.1f}/100</div>
                <div class="detail">🎯 Skill Match: {job.skill_match_score:.1f}/100</div>
            """
            
            if job.remote_type:
                html += f'<div class="detail">📍 {job.remote_type.value}</div>'
            
            if job.stipend_salary:
                html += f'<div class="detail">💰 {job.stipend_salary}</div>'
            
            html += f'<a href="{job.url}" class="link">Apply Now</a>'
            html += "</div>"
        
        html += """
        </body>
        </html>
        """
        
        return html


class AlertManager:
    """Manage all alert channels."""
    
    def __init__(self):
        """Initialize alert manager."""
        self.console = ConsoleAlerter()
        self.email = EmailAlerter()
    
    def send_alerts(self, jobs: List[Job]):
        """
        Send alerts through all enabled channels.
        
        Args:
            jobs: List of jobs to alert about
        """
        # Console alerts
        self.console.send_alerts(jobs)
        
        # Email alerts
        self.email.send_alerts(jobs)
