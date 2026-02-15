"""
Command-line interface for job discovery system.
"""
import argparse
import sys
import logging
from pathlib import Path
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from tabulate import tabulate

from .engine import JobDiscoveryEngine
from .scheduler import DiscoveryScheduler
from .models import Job, RemoteType
from .utils import get_config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
console = Console()


def cmd_search(args):
    """Run one-time search."""
    console.print("[bold blue]Starting job discovery search...[/bold blue]")
    
    engine = JobDiscoveryEngine()
    jobs = engine.discover()
    
    console.print(f"[green]✓ Found {len(jobs)} opportunities[/green]")
    
    # Display results
    if jobs:
        display_jobs(jobs[:20])  # Show top 20
    
    # Send alerts for new jobs
    engine.send_alerts()


def cmd_run(args):
    """Run scheduled discovery loop."""
    console.print("[bold blue]Starting scheduled job discovery...[/bold blue]")
    console.print("Press Ctrl+C to stop\n")
    
    engine = JobDiscoveryEngine()
    scheduler = DiscoveryScheduler()
    
    # Schedule discovery based on config
    config = get_config()
    default_interval = config.get('scheduling.default_frequency_hours', 6)
    
    scheduler.add_job(
        engine.run_discovery_cycle,
        interval_hours=default_interval,
        name="Job Discovery"
    )
    
    # Start scheduler
    scheduler.start()


def cmd_results(args):
    """Show latest results."""
    engine = JobDiscoveryEngine()
    
    if args.new:
        console.print("[bold blue]New jobs since last run:[/bold blue]\n")
        jobs = engine.get_new_jobs()
    else:
        console.print("[bold blue]Top-ranked opportunities:[/bold blue]\n")
        jobs = engine.get_top_jobs(args.limit)
    
    if not jobs:
        console.print("[yellow]No jobs found[/yellow]")
        return
    
    # Display based on format
    if args.format == 'table':
        display_jobs(jobs)
    elif args.format == 'json':
        export_json(jobs, args.output)
    elif args.format == 'csv':
        export_csv(jobs, args.output)


def cmd_configure(args):
    """Configure user profile."""
    config = get_config()
    
    console.print("[bold blue]Configure User Profile[/bold blue]\n")
    
    if args.city:
        config.set('user.city', args.city)
        console.print(f"✓ City set to: {args.city}")
    
    if args.skills:
        skills = args.skills.split(',')
        config.set('user.skills.frameworks', skills)
        console.print(f"✓ Skills set to: {', '.join(skills)}")
    
    if args.city or args.skills:
        config.save()
        console.print("\n[green]Configuration saved![/green]")
    else:
        # Show current config
        console.print(f"City: {config.get('user.city')}")
        console.print(f"Skills: {config.get('user.skills')}")


def cmd_stats(args):
    """Show statistics."""
    engine = JobDiscoveryEngine()
    stats = engine.get_stats()
    
    console.print("\n[bold blue]Job Discovery Statistics[/bold blue]\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")
    
    table.add_row("Total Jobs", str(stats['total_jobs']))
    table.add_row("New Jobs", str(stats['new_jobs']))
    table.add_row("Avg Relevance", f"{stats['avg_relevance']:.1f}")
    
    console.print(table)
    
    if stats.get('by_source'):
        console.print("\n[bold]Jobs by Source:[/bold]")
        for source, count in stats['by_source'].items():
            console.print(f"  {source}: {count}")


def display_jobs(jobs):
    """Display jobs in rich table format."""
    # Group by category
    remote_jobs = [j for j in jobs if j.remote_type in [RemoteType.FULLY_REMOTE, RemoteType.INDIA_REMOTE]]
    nearby_jobs = [j for j in jobs if j not in remote_jobs]
    
    # Display remote jobs
    if remote_jobs:
        console.print("\n[bold green]🌍 Remote Internships & Roles[/bold green]\n")
        _display_job_table(remote_jobs[:10])
    
    # Display nearby jobs
    if nearby_jobs:
        console.print("\n[bold blue]📍 Nearby Opportunities[/bold blue]\n")
        _display_job_table(nearby_jobs[:10])


def _display_job_table(jobs):
    """Display jobs in table."""
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Title", style="cyan", width=30)
    table.add_column("Company", style="yellow", width=20)
    table.add_column("Location", width=15)
    table.add_column("Score", justify="right")
    table.add_column("Skills", width=20)
    
    for job in jobs:
        location = job.remote_type.value if job.remote_type else ', '.join(job.locations[:2])
        skills = ', '.join(job.required_skills[:3]) if job.required_skills else '-'
        
        table.add_row(
            job.title[:30],
            job.company[:20],
            location[:15],
            f"{job.relevance_score:.0f}",
            skills[:20]
        )
    
    console.print(table)


def export_json(jobs, output_path=None):
    """Export jobs to JSON."""
    if output_path is None:
        output_path = "jobs.json"
    
    data = [job.to_dict() for job in jobs]
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    console.print(f"[green]✓ Exported {len(jobs)} jobs to {output_path}[/green]")


def export_csv(jobs, output_path=None):
    """Export jobs to CSV."""
    if output_path is None:
        output_path = "jobs.csv"
    
    import csv
    
    with open(output_path, 'w', newline='') as f:
        if jobs:
            writer = csv.DictWriter(f, fieldnames=jobs[0].to_dict().keys())
            writer.writeheader()
            for job in jobs:
                writer.writerow(job.to_dict())
    
    console.print(f"[green]✓ Exported {len(jobs)} jobs to {output_path}[/green]")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI/ML Job Discovery System",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Search command
    parser_search = subparsers.add_parser('search', help='Run one-time search')
    parser_search.set_defaults(func=cmd_search)
    
    # Run command
    parser_run = subparsers.add_parser('run', help='Start scheduled discovery')
    parser_run.set_defaults(func=cmd_run)
    
    # Results command
    parser_results = subparsers.add_parser('results', help='Show results')
    parser_results.add_argument('--new', action='store_true', help='Show only new jobs')
    parser_results.add_argument('--limit', type=int, default=50, help='Number of results')
    parser_results.add_argument('--format', choices=['table', 'json', 'csv'], 
                               default='table', help='Output format')
    parser_results.add_argument('--output', help='Output file path')
    parser_results.set_defaults(func=cmd_results)
    
    # Configure command
    parser_config = subparsers.add_parser('configure', help='Configure user profile')
    parser_config.add_argument('--city', help='Set your city')
    parser_config.add_argument('--skills', help='Set skills (comma-separated)')
    parser_config.set_defaults(func=cmd_configure)
    
    # Stats command
    parser_stats = subparsers.add_parser('stats', help='Show statistics')
    parser_stats.set_defaults(func=cmd_stats)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute command
    try:
        args.func(args)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        logger.exception("Command failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
