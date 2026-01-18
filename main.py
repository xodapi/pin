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


def main():
    parser = argparse.ArgumentParser(
        description='Pinterest Analytics CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py test              # Test authentication
  python main.py account           # Show account info
  python main.py boards            # List all boards
  python main.py pins              # List recent pins
  python main.py pins -b BOARD_ID  # List pins from board
  python main.py summary           # Show account summary
  python main.py analytics         # Show analytics (Business only)
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
    
    args = parser.parse_args()
    
    if args.command:
        args.func(args)
    else:
        # Default: show help
        parser.print_help()
        console.print("\n[dim]Run 'python main.py test' to verify your setup[/dim]")


if __name__ == '__main__':
    main()
