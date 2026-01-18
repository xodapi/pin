#!/usr/bin/env python3
"""
Pinterest Analytics CLI (Community SDK version)
Main entry point for fetching and reporting Pinterest analytics
"""

import argparse
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def cmd_test(args):
    """Test authentication and basic connectivity"""
    from src.auth import get_auth
    
    console.print("\n[bold blue]Testing Pinterest Authentication[/bold blue]\n")
    
    auth = get_auth()
    
    if not auth.is_configured():
        # Show instructions
        auth._show_setup_instructions()
        return
    
    console.print(f"[green]OK[/green] Access Token: {auth.access_token[:20]}...")
    
    # Test API connectivity
    console.print("\n[bold]Testing API connection...[/bold]")
    
    try:
        from src.analytics import get_analytics
        analytics = get_analytics()
        user = analytics.get_user_account()
        
        console.print(f"[green]OK[/green] Connected to Pinterest API")
        console.print(f"[green]OK[/green] Username: {user.get('username', 'N/A')}")
        console.print(f"[green]OK[/green] Account type: {user.get('account_type', 'N/A')}")
        console.print(f"[green]OK[/green] Followers: {user.get('follower_count', 'N/A')}")
        console.print(f"[green]OK[/green] Pins: {user.get('pin_count', 'N/A')}")
        
        if user.get('account_type') != 'BUSINESS':
            console.print("\n[yellow]Note: Some analytics features require a Business account[/yellow]")
            console.print("[dim]You can convert to Business at: pinterest.com/business/hub/[/dim]")
            
    except Exception as e:
        console.print(f"[red]ERROR[/red] API Error: {e}")


def cmd_account(args):
    """Show account information"""
    from src.analytics import get_analytics
    
    console.print("\n[bold blue]Account Information[/bold blue]\n")
    
    try:
        analytics = get_analytics()
        user = analytics.get_user_account()
        
        table = Table(show_header=False, box=None)
        table.add_column("Field", style="cyan")
        table.add_column("Value")
        
        table.add_row("Username", str(user.get('username', 'N/A')))
        table.add_row("Account Type", str(user.get('account_type', 'N/A')))
        table.add_row("Website", str(user.get('website_url', 'N/A')))
        table.add_row("Followers", str(user.get('follower_count', 'N/A')))
        table.add_row("Following", str(user.get('following_count', 'N/A')))
        table.add_row("Pins", str(user.get('pin_count', 'N/A')))
        table.add_row("Boards", str(user.get('board_count', 'N/A')))
        table.add_row("Monthly Views", str(user.get('monthly_views', 'N/A')))
        
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def cmd_boards(args):
    """List all boards"""
    from src.analytics import get_analytics
    
    console.print("\n[bold blue]Your Boards[/bold blue]\n")
    
    try:
        analytics = get_analytics()
        boards = analytics.get_boards()
        
        if not boards:
            console.print("[yellow]No boards found[/yellow]")
            return
        
        table = Table()
        table.add_column("Name", style="cyan")
        table.add_column("Pins", justify="right")
        table.add_column("Followers", justify="right")
        table.add_column("Privacy")
        table.add_column("ID", style="dim")
        
        for board in boards:
            table.add_row(
                str(board.get('name', 'N/A')),
                str(board.get('pin_count', 0)),
                str(board.get('follower_count', 0)),
                str(board.get('privacy', 'N/A')),
                str(board.get('id', 'N/A')),
            )
        
        console.print(table)
        console.print(f"\n[dim]Total: {len(boards)} boards[/dim]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def cmd_pins(args):
    """List pins"""
    from src.analytics import get_analytics
    
    limit = args.limit or 25
    console.print(f"\n[bold blue]Your Pins (showing {limit})[/bold blue]\n")
    
    try:
        analytics = get_analytics()
        
        if args.board:
            pins = analytics.get_board_pins(args.board, page_size=limit)
            console.print(f"[dim]From board: {args.board}[/dim]\n")
        else:
            pins = analytics.get_pins(page_size=limit)
        
        if not pins:
            console.print("[yellow]No pins found[/yellow]")
            return
        
        table = Table()
        table.add_column("Title", style="cyan", max_width=40)
        table.add_column("Created", style="dim")
        table.add_column("ID")
        
        for pin in pins[:limit]:
            title = pin.get('title') or pin.get('description', '')[:40] or 'No title'
            created = str(pin.get('created_at', 'N/A'))[:10]
            table.add_row(
                title[:40],
                created,
                str(pin.get('id', 'N/A')),
            )
        
        console.print(table)
        console.print(f"\n[dim]Showing {len(pins)} pins[/dim]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def cmd_analytics(args):
    """Show account analytics (requires Business account)"""
    from src.analytics import get_analytics
    
    console.print("\n[bold blue]Account Analytics[/bold blue]\n")
    
    try:
        analytics = get_analytics()
        data = analytics.get_user_analytics()
        
        if 'error' in data:
            console.print(f"[yellow]Warning: {data.get('note', data['error'])}[/yellow]")
            console.print("\n[dim]Showing basic account summary instead:[/dim]\n")
            
            # Show summary instead
            summary = analytics.get_summary()
            
            table = Table()
            table.add_column("Metric", style="cyan")
            table.add_column("Value", justify="right")
            
            table.add_row("Username", str(summary['account'].get('username', 'N/A')))
            table.add_row("Account Type", str(summary['account'].get('account_type', 'N/A')))
            table.add_row("Total Boards", str(summary['boards_count']))
            table.add_row("Total Pins", str(summary['total_pins']))
            table.add_row("Total Board Followers", str(summary['total_followers']))
            table.add_row("Monthly Views", str(summary['account'].get('monthly_views', 'N/A')))
            
            console.print(table)
        else:
            console.print(json.dumps(data, indent=2, default=str))
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def cmd_summary(args):
    """Show account summary"""
    from src.analytics import get_analytics
    
    console.print("\n[bold blue]Account Summary[/bold blue]\n")
    
    try:
        analytics = get_analytics()
        summary = analytics.get_summary()
        
        # Account info
        account = summary['account']
        console.print(Panel(
            f"[bold]{account.get('username', 'Unknown')}[/bold]\n"
            f"Type: {account.get('account_type', 'N/A')}\n"
            f"Followers: {account.get('follower_count', 0)}\n"
            f"Monthly Views: {account.get('monthly_views', 'N/A')}",
            title="Account"
        ))
        
        # Stats
        table = Table(title="Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right")
        
        table.add_row("Boards", str(summary['boards_count']))
        table.add_row("Total Pins", str(summary['total_pins']))
        table.add_row("Total Board Followers", str(summary['total_followers']))
        
        console.print(table)
        
        # Top boards
        if summary['boards']:
            console.print("\n[bold]Top Boards by Pins:[/bold]")
            sorted_boards = sorted(summary['boards'], key=lambda x: x.get('pin_count', 0) or 0, reverse=True)[:5]
            for i, board in enumerate(sorted_boards, 1):
                console.print(f"  {i}. {board.get('name', 'N/A')} ({board.get('pin_count', 0)} pins)")
                
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def cmd_export(args):
    """Export data to file"""
    from src.analytics import get_analytics
    from src.report import get_report_generator
    
    report_type = args.type or 'summary'
    format = args.format or 'json'
    
    console.print(f"\n[bold blue]Exporting {report_type} ({format})[/bold blue]\n")
    
    try:
        reporter = get_report_generator()
        
        if report_type == 'summary':
            filepath = reporter.generate_summary_report(format=format)
        elif report_type == 'boards':
            filepath = reporter.generate_boards_report(format=format)
        elif report_type == 'pins':
            filepath = reporter.generate_pins_report(format=format)
        elif report_type == 'all':
            filepath = reporter.generate_full_report(format=format)
        else:
            console.print(f"[red]Unknown report type: {report_type}[/red]")
            return
            
        console.print(f"\n[green]Saved to:[/green] {filepath}")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise


def cmd_dashboard(args):
    """Open web dashboard"""
    from src.analytics import get_analytics
    from src.dashboard import start_dashboard
    
    port = args.port or 8080
    console.print(f"\n[bold blue]Starting Dashboard[/bold blue]\n")
    
    try:
        analytics = get_analytics()
        start_dashboard(analytics, port=port)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def cmd_evening(args):
    """Generate evening report"""
    from src.analytics import get_analytics
    from src.daily_report import get_daily_report
    
    console.print(f"\n[bold blue]Evening Report[/bold blue]\n")
    
    try:
        analytics = get_analytics()
        reporter = get_daily_report()
        report = reporter.generate_evening_report(analytics)
        
        # Display report
        if 'error' in report:
            console.print(f"[red]Error: {report['error']}[/red]")
            return
        
        # Health status
        health = report.get('health_status', {})
        status_color = 'green' if health.get('overall') == 'OK' else 'yellow' if health.get('overall') == 'WARNING' else 'red'
        console.print(f"[{status_color}]Health: {health.get('overall', 'Unknown')}[/{status_color}]")
        
        for check in health.get('checks', []):
            icon = '[green]OK[/green]' if check.get('status') == 'OK' else '[yellow]![/yellow]' if check.get('status') == 'WARNING' else '[red]X[/red]'
            msg = check.get('message', '')
            console.print(f"  {icon} {check.get('name')}{': ' + msg if msg else ''}")
        
        # Alerts
        alerts = report.get('alerts', [])
        if alerts:
            console.print("\n[bold]Alerts:[/bold]")
            for alert in alerts:
                color = 'yellow' if alert.get('type') == 'WARNING' else 'green' if alert.get('type') == 'SUCCESS' else 'blue'
                console.print(f"  [{color}]{alert.get('message')}[/{color}]")
        
        # Comparison
        vs_yesterday = report.get('vs_yesterday')
        if vs_yesterday and 'no_previous_data' not in vs_yesterday:
            console.print("\n[bold]vs Yesterday:[/bold]")
            for key, data in vs_yesterday.items():
                change = data.get('change_percent', 0)
                arrow = '+' if change > 0 else ''
                color = 'green' if change > 0 else 'red' if change < 0 else 'white'
                console.print(f"  {key}: [{color}]{arrow}{change}%[/{color}]")
        
        console.print(f"\n[dim]Report saved to data/history/{report.get('date')}.json[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def cmd_cleanup(args):
    """Find underperforming pins for cleanup"""
    from src.bulk_analyzer import get_bulk_analyzer
    
    days = args.days or 180
    min_saves = args.min_saves or 1000
    
    console.print(f"\n[bold blue]Cleanup Analysis[/bold blue]")
    console.print(f"[dim]Finding pins older than {days} days[/dim]\n")
    
    try:
        analyzer = get_bulk_analyzer()
        result = analyzer.find_underperforming(min_saves=min_saves, days=days)
        
        summary = result.get('summary', {})
        
        # Display summary
        table = Table(title="Cleanup Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right")
        
        table.add_row("Total Pins", f"{summary.get('total_pins', 0):,}")
        table.add_row("Old Pins (for cleanup)", f"[yellow]{summary.get('old_pins', 0):,}[/yellow]")
        table.add_row("New Pins (keep)", f"[green]{summary.get('new_pins', 0):,}[/green]")
        table.add_row("Percentage to cleanup", f"{summary.get('percentage_old', 0)}%")
        
        console.print(table)
        
        # Show by board
        by_board = result.get('by_board', {})
        if by_board:
            console.print("\n[bold]Old pins by board:[/bold]")
            sorted_boards = sorted(by_board.items(), key=lambda x: x[1], reverse=True)
            for board, count in sorted_boards[:10]:
                console.print(f"  {board}: {count} pins")
        
        # Export option
        if result.get('pins'):
            console.print(f"\n[dim]Found {len(result['pins'])} pins for potential cleanup[/dim]")
            
            if args.export:
                filepath = analyzer.export_cleanup_list(
                    result['pins'],
                    format=args.export
                )
                console.print(f"[green]Exported to:[/green] {filepath}")
        
        console.print(f"\n[dim]Note: {result.get('note', '')}[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def cmd_trends(args):
    """Analyze trends and find what's working"""
    from src.trends_analyzer import get_trends_analyzer
    
    console.print(f"\n[bold blue]Trends Analysis[/bold blue]\n")
    
    try:
        analyzer = get_trends_analyzer()
        
        # Boards performance
        console.print("[bold]Analyzing boards...[/bold]")
        boards = analyzer.analyze_boards_performance()
        
        if 'summary' in boards:
            s = boards['summary']
            console.print(f"  Total: {s.get('total_pins', 0):,} pins in {s.get('total_boards', 0)} boards")
            console.print(f"  Followers: {s.get('total_followers', 0):,}")
        
        if boards.get('most_efficient'):
            console.print("\n[bold]Most Efficient Boards:[/bold] (followers per pin)")
            for b in boards['most_efficient'][:5]:
                console.print(f"  {b.get('name')}: {b.get('efficiency', 0):.1f} ({b.get('pins')} pins, {b.get('followers')} followers)")
        
        if boards.get('recommendations'):
            console.print("\n[bold]Recommendations:[/bold]")
            for rec in boards['recommendations']:
                console.print(f"  [yellow]>[/yellow] {rec}")
        
        # Niche
        console.print("\n[bold]Analyzing niche...[/bold]")
        niche = analyzer.find_niche()
        
        if niche.get('top_board_niche'):
            console.print(f"\n[green]Your Niche:[/green] {niche.get('top_board_niche')}")
        
        if niche.get('top_keywords'):
            console.print(f"[green]Top Keywords:[/green] {', '.join(niche.get('top_keywords', []))}")
        
        if niche.get('recommendation'):
            console.print(f"\n[cyan]{niche.get('recommendation')}[/cyan]")
        
        # Posting patterns
        if args.full:
            console.print("\n[bold]Analyzing posting patterns...[/bold]")
            patterns = analyzer.analyze_posting_patterns()
            
            if patterns.get('best_days'):
                console.print(f"  Best days: {', '.join([d['day'] for d in patterns['best_days']])}")
            if patterns.get('best_hours'):
                console.print(f"  Best hours: {', '.join([str(h['hour']) + ':00' for h in patterns['best_hours'][:3]])}")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()


def cmd_backup(args):
    """Backup all pins and boards locally"""
    from src.backup import get_backup_manager
    
    include_images = args.images if hasattr(args, 'images') else False
    
    console.print(f"\n[bold blue]Creating Backup[/bold blue]")
    if include_images:
        console.print("[dim]Including images (this will take longer)[/dim]")
    console.print("")
    
    try:
        manager = get_backup_manager()
        result = manager.create_backup(include_images=include_images)
        
        console.print(f"\n[green]Backup complete![/green]")
        console.print(f"  Path: {result['path']}")
        console.print(f"  Boards: {len(result['boards'])}")
        console.print(f"  Pins: {len(result['pins'])}")
        if include_images:
            console.print(f"  Images: {result['images_downloaded']}")
        
        if result['errors']:
            console.print(f"\n[yellow]Warnings:[/yellow]")
            for error in result['errors']:
                console.print(f"  {error}")
                
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def cmd_backup_list(args):
    """List available backups"""
    from src.backup import get_backup_manager
    
    console.print(f"\n[bold blue]Available Backups[/bold blue]\n")
    
    try:
        manager = get_backup_manager()
        backups = manager.list_backups()
        
        if not backups:
            console.print("[yellow]No backups found[/yellow]")
            console.print("[dim]Create one with: python main.py backup[/dim]")
            return
        
        table = Table()
        table.add_column("Date", style="cyan")
        table.add_column("Pins", justify="right")
        table.add_column("Boards", justify="right")
        table.add_column("Images", justify="right")
        table.add_column("Folder")
        
        for b in backups:
            table.add_row(
                b.get('created_at', '')[:19],
                str(b.get('total_pins', 0)),
                str(b.get('total_boards', 0)),
                str(b.get('images_downloaded', 0)),
                b.get('folder', ''),
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def cmd_quick(args):
    """Quick 30-second status report"""
    from src.quick_report import get_quick_report
    
    try:
        reporter = get_quick_report()
        report = reporter.generate()
        
        # Use formatted output
        console.print(reporter.format_cli(report))
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def cmd_keywords(args):
    """Analyze keywords for SEO"""
    from src.keywords import get_keyword_analyzer
    
    console.print(f"\n[bold blue]Keyword Analysis[/bold blue]\n")
    
    try:
        analyzer = get_keyword_analyzer()
        
        if args.check:
            # Check specific keyword
            result = analyzer.check_keyword(args.check)
            
            console.print(f"Keyword: [cyan]{result['keyword']}[/cyan]")
            console.print(f"Coverage: {result['coverage']}% ({result['matching_pins']}/{result['total_pins']} pins)")
            console.print(f"  In titles: {result['in_title']}")
            console.print(f"  In descriptions: {result['in_description']}")
            console.print(f"\n[dim]{result['recommendation']}[/dim]")
        else:
            # Full keyword analysis
            console.print("[dim]Analyzing your pins...[/dim]\n")
            result = analyzer.analyze_my_keywords()
            
            if 'error' in result:
                console.print(f"[red]{result['error']}[/red]")
                return
            
            console.print(f"Analyzed: {result['total_pins_analyzed']} pins")
            console.print(f"Unique keywords: {result['unique_keywords']}")
            
            # Top keywords
            console.print("\n[bold]Top Keywords:[/bold]")
            for kw in result['top_keywords'][:15]:
                bar = '█' * min(int(kw['frequency']), 20)
                console.print(f"  {kw['keyword']}: {kw['count']} ({kw['frequency']}%) {bar}")
            
            # Recommendations
            if result.get('recommendations'):
                console.print("\n[bold]Recommendations:[/bold]")
                for rec in result['recommendations']:
                    console.print(f"  [yellow]>[/yellow] {rec}")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()


def cmd_links(args):
    """Check for broken links in pins"""
    from src.link_checker import get_link_checker
    
    console.print(f"\n[bold blue]Link Checker[/bold blue]\n")
    console.print("[dim]Checking links in your pins...[/dim]\n")
    
    try:
        checker = get_link_checker()
        result = checker.check_all_links()
        
        if 'error' in result:
            console.print(f"[red]{result['error']}[/red]")
            return
        
        summary = result.get('summary', {})
        
        # Stats
        console.print(f"[bold]Results:[/bold]")
        console.print(f"  Unique links checked: {result.get('unique_links', 0)}")
        console.print(f"  [green]Working: {summary.get('working_count', 0)}[/green]")
        console.print(f"  [red]Broken: {summary.get('broken_count', 0)}[/red]")
        console.print(f"  [yellow]Redirects: {summary.get('redirect_count', 0)}[/yellow]")
        console.print(f"  Health Score: {summary.get('health_score', 0)}%")
        
        # Broken links
        if result.get('broken'):
            console.print(f"\n[bold red]Broken Links:[/bold red]")
            for item in result['broken'][:10]:
                console.print(f"  [red]✗[/red] {item['url'][:60]}...")
                console.print(f"    Error: {item.get('error', 'Unknown')}")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def cmd_templates(args):
    """Show description templates"""
    from src.templates import get_description_helper
    
    console.print(f"\n[bold blue]Description Templates[/bold blue]\n")
    
    try:
        helper = get_description_helper()
        
        if args.analyze:
            # Analyze a description
            result = helper.analyze_description(args.analyze)
            
            console.print(f"[bold]Analysis:[/bold]")
            console.print(f"  Score: {result['score']}/100 ({result['rating']})")
            console.print(f"  Length: {result['length']} chars")
            console.print(f"  Hashtags: {result['hashtag_count']}")
            
            if result['issues']:
                console.print(f"\n[bold red]Issues:[/bold red]")
                for issue in result['issues']:
                    console.print(f"  [red]✗[/red] {issue}")
            
            if result['suggestions']:
                console.print(f"\n[bold yellow]Suggestions:[/bold yellow]")
                for sug in result['suggestions']:
                    console.print(f"  [yellow]>[/yellow] {sug}")
        else:
            # Show templates
            templates = helper.get_templates()
            
            table = Table(title="Available Templates")
            table.add_column("Type", style="cyan")
            table.add_column("Example")
            
            for t in templates:
                table.add_row(t['name'], t['example'][:80] + "...")
            
            console.print(table)
            console.print("\n[dim]Tip: Use --analyze 'your description' to check SEO quality[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def cmd_health(args):
    """Show account health score"""
    from src.math_analytics import get_math_analytics
    
    console.print(f"\n[bold blue]Account Health Report[/bold blue]\n")
    
    try:
        math = get_math_analytics()
        report = math.generate_health_report()
        
        if 'error' in report:
            console.print(f"[red]{report['error']}[/red]")
            return
        
        # Overall score
        console.print(f"[bold]Overall Score: {report['overall_score']}/100 ({report['rating']}) {report['emoji']}[/bold]")
        console.print(f"Grade: [cyan]{report['grade']}[/cyan]\n")
        
        # Individual scores
        console.print("[bold]Component Scores:[/bold]")
        for metric, score in report['scores'].items():
            bar = '█' * (score // 10)
            empty = '░' * (10 - score // 10)
            color = 'green' if score >= 70 else 'yellow' if score >= 40 else 'red'
            console.print(f"  {metric.capitalize():12} [{color}]{bar}{empty}[/{color}] {score}/100")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def cmd_math(args):
    """Show mathematical analytics"""
    from src.math_analytics import get_math_analytics
    
    console.print(f"\n[bold blue]Mathematical Analytics[/bold blue]\n")
    
    try:
        math = get_math_analytics()
        
        if args.boards:
            # Board analysis
            result = math.analyze_boards_math()
            
            if 'error' in result:
                console.print(f"[red]{result['error']}[/red]")
                return
            
            stats = result['statistics']
            console.print("[bold]Board Statistics:[/bold]")
            console.print(f"  Total Boards: {stats['total_boards']}")
            console.print(f"  Total Pins: {stats['total_pins']:,}")
            console.print(f"  Avg Pins/Board: {stats['avg_pins_per_board']}")
            console.print(f"  Avg Efficiency: {stats.get('avg_efficiency', 0)}")
            console.print(f"  Std Deviation: {stats.get('std_deviation', 0)}")
            
            console.print("\n[bold]Top Efficient Boards:[/bold]")
            for b in result.get('top_efficient', [])[:5]:
                console.print(f"  [green]★[/green] {b['name']}: {b['efficiency']} ({b['efficiency_rating']})")
            
            if result.get('recommendations'):
                console.print("\n[bold]Recommendations:[/bold]")
                for rec in result['recommendations']:
                    console.print(f"  [yellow]>[/yellow] {rec}")
        
        elif args.pins:
            # Pin analysis
            result = math.analyze_pins_math(days=args.days or 30)
            
            if 'error' in result:
                console.print(f"[red]{result['error']}[/red]")
                return
            
            console.print("[bold]Pin Statistics:[/bold]")
            console.print(f"  Total Pins: {result['total_pins']:,}")
            console.print(f"  Recent (last {args.days or 30} days): {result['recent_pins']}")
            console.print(f"  Posts/Day: {result['posts_per_day']}")
            console.print(f"  Activity: {result['activity_rating']}")
            console.print(f"  Trend: {result['trend']} ({result['trend_change_percent']:+}%)")
            
            if result.get('best_days'):
                days_str = ', '.join([d['day'] for d in result['best_days']])
                console.print(f"  Best Days: {days_str}")
        
        else:
            # Quick health check
            health = math.generate_health_report()
            console.print(f"Health Score: {health['overall_score']}/100 ({health['grade']})")
            console.print("\n[dim]Use --boards or --pins for detailed analysis[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()


def cmd_top(args):
    """Show top pins"""
    from src.compare import get_top_pins
    
    limit = args.limit or 10
    days = args.days
    
    console.print(f"\n[bold blue]Top {limit} Pins[/bold blue]")
    if days:
        console.print(f"[dim]Last {days} days[/dim]")
    console.print("")
    
    try:
        top = get_top_pins()
        
        if args.boards:
            # Top by board
            result = top.get_top_by_board(limit=limit)
            
            if 'error' in result:
                console.print(f"[red]{result['error']}[/red]")
                return
            
            table = Table(title=f"Top {limit} Boards")
            table.add_column("#", style="cyan")
            table.add_column("Board")
            table.add_column("Pins", justify="right")
            table.add_column("Latest Pin")
            
            for i, item in enumerate(result['results']):
                table.add_row(
                    str(i + 1),
                    item['board_name'],
                    str(item['total_pins']),
                    item['top_pin']['title'][:30],
                )
            
            console.print(table)
        else:
            # Top pins
            result = top.get_top_pins(limit=limit, days=days)
            
            if 'error' in result:
                console.print(f"[red]{result['error']}[/red]")
                return
            
            table = Table(title=f"Top {limit} Pins")
            table.add_column("#", style="cyan")
            table.add_column("Title")
            table.add_column("Created")
            table.add_column("Link")
            
            for pin in result['pins']:
                created = str(pin.get('created_at', ''))[:10]
                link = pin.get('link', '')[:30] + '...' if pin.get('link') else '-'
                table.add_row(
                    str(pin['rank']),
                    pin['title'] or 'Untitled',
                    created,
                    link,
                )
            
            console.print(table)
            console.print(f"\n[dim]Total analyzed: {result['total_analyzed']} pins[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def cmd_compare(args):
    """Compare periods"""
    from src.compare import get_period_compare
    
    console.print(f"\n[bold blue]Period Comparison[/bold blue]\n")
    
    try:
        compare = get_period_compare()
        
        # Determine comparison type
        if args.weeks:
            result = compare.compare_weeks(weeks_back=args.weeks)
            title = f"This week vs {args.weeks} week(s) ago"
        elif args.months:
            result = compare.compare_months(months_back=args.months)
            title = f"This month vs {args.months} month(s) ago"
        else:
            days = args.days or 7
            result = compare.compare_custom_days(days=days)
            title = f"Last {days} days vs previous {days} days"
        
        console.print(f"[bold]{title}[/bold]\n")
        
        # Show comparison table
        table = Table()
        table.add_column("Metric")
        table.add_column(result['period1']['name'], justify="right")
        table.add_column(result['period2']['name'], justify="right")
        table.add_column("Change", justify="right")
        
        for metric, data in result['changes'].items():
            trend_icon = '↑' if data['trend'] == 'up' else '↓' if data['trend'] == 'down' else '→'
            color = 'green' if data['trend'] == 'up' else 'red' if data['trend'] == 'down' else 'white'
            
            change_str = f"[{color}]{trend_icon} {data['change_percent']:+}%[/{color}]"
            
            table.add_row(
                metric.replace('_', ' ').title(),
                str(data['old']),
                str(data['new']),
                change_str,
            )
        
        console.print(table)
        console.print(f"\n[cyan]{result['summary']}[/cyan]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()


def main():
    parser = argparse.ArgumentParser(
        description='Pinterest Analytics CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py test              # Test authentication
  python main.py quick             # Quick 30-second status
  python main.py dashboard         # Open web dashboard
  python main.py backup            # Backup all pins locally
  python main.py backup --images   # Backup with images
  python main.py cleanup           # Find underperforming pins
  python main.py trends            # Find your niche  
  python main.py keywords          # Analyze keywords for SEO
  python main.py keywords -c art   # Check specific keyword
  python main.py evening           # Generate evening report
  python main.py export -t all     # Export all data to JSON
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test authentication')
    test_parser.set_defaults(func=cmd_test)
    
    # Account command
    account_parser = subparsers.add_parser('account', help='Show account info')
    account_parser.set_defaults(func=cmd_account)
    
    # Boards command
    boards_parser = subparsers.add_parser('boards', help='List boards')
    boards_parser.set_defaults(func=cmd_boards)
    
    # Pins command
    pins_parser = subparsers.add_parser('pins', help='List pins')
    pins_parser.add_argument('-n', '--limit', type=int, default=25, help='Number of pins')
    pins_parser.add_argument('-b', '--board', help='Board ID to list pins from')
    pins_parser.set_defaults(func=cmd_pins)
    
    # Summary command
    summary_parser = subparsers.add_parser('summary', help='Show account summary')
    summary_parser.set_defaults(func=cmd_summary)
    
    # Analytics command
    analytics_parser = subparsers.add_parser('analytics', help='Show analytics (Business account)')
    analytics_parser.set_defaults(func=cmd_analytics)
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export data to file')
    export_parser.add_argument(
        '-t', '--type', 
        choices=['summary', 'boards', 'pins', 'all'],
        default='summary',
        help='Data to export'
    )
    export_parser.add_argument(
        '-f', '--format',
        choices=['json', 'csv', 'excel'],
        default='json',
        help='Output format'
    )
    export_parser.set_defaults(func=cmd_export)
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser('dashboard', help='Open web dashboard')
    dashboard_parser.add_argument('-p', '--port', type=int, default=8080, help='Port number')
    dashboard_parser.set_defaults(func=cmd_dashboard)
    
    # Evening report command
    report_parser = subparsers.add_parser('evening', help='Generate evening report')
    report_parser.set_defaults(func=cmd_evening)
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Find underperforming pins')
    cleanup_parser.add_argument('-d', '--days', type=int, default=180, help='Pins older than N days')
    cleanup_parser.add_argument('-s', '--min-saves', type=int, default=1000, help='Minimum saves threshold')
    cleanup_parser.add_argument('-e', '--export', choices=['json', 'csv', 'txt'], help='Export list to file')
    cleanup_parser.set_defaults(func=cmd_cleanup)
    
    # Trends command
    trends_parser = subparsers.add_parser('trends', help='Analyze trends and find niche')
    trends_parser.add_argument('--full', action='store_true', help='Show full analysis with posting patterns')
    trends_parser.set_defaults(func=cmd_trends)
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Backup pins and boards locally')
    backup_parser.add_argument('--images', action='store_true', help='Also download images')
    backup_parser.add_argument('--list', action='store_true', help='List available backups')
    backup_parser.set_defaults(func=cmd_backup)
    
    # Backup list subcommand
    backup_list_parser = subparsers.add_parser('backups', help='List available backups')
    backup_list_parser.set_defaults(func=cmd_backup_list)
    
    # Quick report command
    quick_parser = subparsers.add_parser('quick', help='Quick 30-second status')
    quick_parser.set_defaults(func=cmd_quick)
    
    # Keywords command
    keywords_parser = subparsers.add_parser('keywords', help='Analyze keywords for SEO')
    keywords_parser.add_argument('-c', '--check', type=str, help='Check specific keyword')
    keywords_parser.set_defaults(func=cmd_keywords)
    
    # Links command
    links_parser = subparsers.add_parser('links', help='Check for broken links')
    links_parser.set_defaults(func=cmd_links)
    
    # Templates command
    templates_parser = subparsers.add_parser('templates', help='Description templates for SEO')
    templates_parser.add_argument('-a', '--analyze', type=str, help='Analyze description quality')
    templates_parser.set_defaults(func=cmd_templates)
    
    # Health command
    health_parser = subparsers.add_parser('health', help='Account health score (A-F)')
    health_parser.set_defaults(func=cmd_health)
    
    # Math analytics command
    math_parser = subparsers.add_parser('math', help='Mathematical analytics')
    math_parser.add_argument('--boards', action='store_true', help='Analyze boards efficiency')
    math_parser.add_argument('--pins', action='store_true', help='Analyze pins trends')
    math_parser.add_argument('-d', '--days', type=int, default=30, help='Analysis period in days')
    math_parser.set_defaults(func=cmd_math)
    
    # Top pins command
    top_parser = subparsers.add_parser('top', help='Show top pins')
    top_parser.add_argument('-n', '--limit', type=int, default=10, help='Number of pins to show')
    top_parser.add_argument('-d', '--days', type=int, help='Filter to last N days')
    top_parser.add_argument('--boards', action='store_true', help='Show top boards instead')
    top_parser.set_defaults(func=cmd_top)
    
    # Compare periods command
    compare_parser = subparsers.add_parser('compare', help='Compare periods')
    compare_parser.add_argument('-d', '--days', type=int, help='Compare last N days vs previous N days')
    compare_parser.add_argument('-w', '--weeks', type=int, help='Compare this week vs N weeks ago')
    compare_parser.add_argument('-m', '--months', type=int, help='Compare this month vs N months ago')
    compare_parser.set_defaults(func=cmd_compare)
    
    args = parser.parse_args()
    
    if args.command:
        args.func(args)
    else:
        # Default: show help
        parser.print_help()
        console.print("\n[dim]First time? Run: python setup.py[/dim]")
        console.print("[dim]Quick start: python main.py quick[/dim]")


if __name__ == '__main__':
    main()
