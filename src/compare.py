"""
Pinterest Compare Tool
Compare metrics between configurable periods
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import json

from .analytics import get_analytics
from .bulk_analyzer import get_bulk_analyzer
from .daily_report import get_daily_report


class PeriodCompare:
    """Compare Pinterest metrics between periods"""
    
    def __init__(self):
        self.analytics = get_analytics()
        self.bulk = get_bulk_analyzer()
        self.daily = get_daily_report()
        self.history_dir = Path('data/history')
        
    def compare_periods(
        self,
        period1_start: datetime,
        period1_end: datetime,
        period2_start: datetime,
        period2_end: datetime,
        period1_name: str = "Period 1",
        period2_name: str = "Period 2"
    ) -> Dict[str, Any]:
        """
        Compare two custom periods
        
        Args:
            period1_start, period1_end: First period dates
            period2_start, period2_end: Second period dates
            period1_name, period2_name: Optional period labels
            
        Returns:
            Comparison results with changes
        """
        # Get pins in each period
        all_pins = self.bulk.get_all_pins()
        
        period1_pins = self._filter_pins_by_date(all_pins, period1_start, period1_end)
        period2_pins = self._filter_pins_by_date(all_pins, period2_start, period2_end)
        
        # Calculate metrics for each period
        metrics1 = self._calculate_period_metrics(period1_pins, period1_name)
        metrics2 = self._calculate_period_metrics(period2_pins, period2_name)
        
        # Calculate changes
        changes = self._calculate_changes(metrics1, metrics2)
        
        return {
            'period1': {
                'name': period1_name,
                'start': period1_start.isoformat(),
                'end': period1_end.isoformat(),
                'metrics': metrics1,
            },
            'period2': {
                'name': period2_name,
                'start': period2_start.isoformat(),
                'end': period2_end.isoformat(),
                'metrics': metrics2,
            },
            'changes': changes,
            'summary': self._generate_summary(changes),
        }
    
    def compare_weeks(self, weeks_back: int = 1) -> Dict[str, Any]:
        """
        Compare this week vs N weeks ago
        
        Args:
            weeks_back: How many weeks back to compare
            
        Returns:
            Week comparison results
        """
        now = datetime.now()
        
        # This week (Mon-Sun)
        this_week_start = now - timedelta(days=now.weekday())
        this_week_start = this_week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        this_week_end = now
        
        # Previous week
        prev_week_start = this_week_start - timedelta(weeks=weeks_back)
        prev_week_end = prev_week_start + timedelta(days=6, hours=23, minutes=59)
        
        return self.compare_periods(
            prev_week_start, prev_week_end,
            this_week_start, this_week_end,
            f"{weeks_back} week(s) ago",
            "This week"
        )
    
    def compare_months(self, months_back: int = 1) -> Dict[str, Any]:
        """
        Compare this month vs N months ago
        
        Args:
            months_back: How many months back to compare
            
        Returns:
            Month comparison results
        """
        now = datetime.now()
        
        # This month
        this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        this_month_end = now
        
        # Previous month
        prev_month = this_month_start
        for _ in range(months_back):
            prev_month = (prev_month - timedelta(days=1)).replace(day=1)
        
        # End of previous month
        prev_month_end = this_month_start - timedelta(days=1)
        for _ in range(months_back - 1):
            prev_month_end = (prev_month_end.replace(day=1) - timedelta(days=1))
        
        return self.compare_periods(
            prev_month, prev_month_end,
            this_month_start, this_month_end,
            f"{months_back} month(s) ago",
            "This month"
        )
    
    def compare_custom_days(self, days: int = 7) -> Dict[str, Any]:
        """
        Compare last N days vs previous N days
        
        Args:
            days: Number of days in each period
            
        Returns:
            Comparison results
        """
        now = datetime.now()
        
        # Recent period
        recent_end = now
        recent_start = now - timedelta(days=days)
        
        # Previous period
        prev_end = recent_start
        prev_start = prev_end - timedelta(days=days)
        
        return self.compare_periods(
            prev_start, prev_end,
            recent_start, recent_end,
            f"Previous {days} days",
            f"Last {days} days"
        )
    
    def _filter_pins_by_date(
        self, 
        pins: List[Dict], 
        start: datetime, 
        end: datetime
    ) -> List[Dict]:
        """Filter pins by creation date"""
        filtered = []
        
        for pin in pins:
            created = pin.get('created_at')
            if created:
                try:
                    if isinstance(created, str):
                        dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                        dt = dt.replace(tzinfo=None)
                    else:
                        dt = created
                    
                    if start <= dt <= end:
                        filtered.append(pin)
                except:
                    pass
        
        return filtered
    
    def _calculate_period_metrics(self, pins: List[Dict], name: str) -> Dict[str, Any]:
        """Calculate metrics for a period"""
        return {
            'pins_created': len(pins),
            'boards_used': len(set(p.get('board_id') for p in pins if p.get('board_id'))),
            'avg_pins_per_day': round(len(pins) / max(1, 7), 2),  # Approximate
        }
    
    def _calculate_changes(self, old: Dict, new: Dict) -> Dict[str, Any]:
        """Calculate changes between periods"""
        changes = {}
        
        for key in ['pins_created', 'boards_used', 'avg_pins_per_day']:
            old_val = old.get(key, 0)
            new_val = new.get(key, 0)
            
            if old_val > 0:
                change_pct = ((new_val - old_val) / old_val) * 100
            else:
                change_pct = 100 if new_val > 0 else 0
            
            changes[key] = {
                'old': old_val,
                'new': new_val,
                'change': new_val - old_val,
                'change_percent': round(change_pct, 1),
                'trend': 'up' if new_val > old_val else 'down' if new_val < old_val else 'stable',
            }
        
        return changes
    
    def _generate_summary(self, changes: Dict) -> str:
        """Generate human-readable summary"""
        pins_change = changes.get('pins_created', {})
        
        if pins_change.get('trend') == 'up':
            return f"Activity increased by {pins_change['change_percent']}%"
        elif pins_change.get('trend') == 'down':
            return f"Activity decreased by {abs(pins_change['change_percent'])}%"
        else:
            return "Activity remained stable"


class TopPins:
    """Find top performing pins"""
    
    def __init__(self):
        self.analytics = get_analytics()
        self.bulk = get_bulk_analyzer()
        
    def get_top_pins(
        self,
        limit: int = 10,
        sort_by: str = 'date',
        days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get top performing pins
        
        Args:
            limit: Number of pins to return
            sort_by: Sort criteria ('date', 'board')
            days: Filter to last N days (None for all time)
            
        Returns:
            Top pins with metrics
        """
        pins = self.bulk.get_all_pins()
        
        if not pins:
            return {'error': 'No pins found', 'pins': []}
        
        # Filter by date if specified
        if days:
            cutoff = datetime.now() - timedelta(days=days)
            filtered = []
            for pin in pins:
                created = pin.get('created_at')
                if created:
                    try:
                        if isinstance(created, str):
                            dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                            dt = dt.replace(tzinfo=None)
                        else:
                            dt = created
                        if dt >= cutoff:
                            filtered.append(pin)
                    except:
                        filtered.append(pin)
                else:
                    filtered.append(pin)
            pins = filtered
        
        # Sort pins
        if sort_by == 'date':
            pins = sorted(pins, key=lambda x: x.get('created_at', ''), reverse=True)
        elif sort_by == 'board':
            pins = sorted(pins, key=lambda x: x.get('board_id', ''))
        
        # Take top N
        top = pins[:limit]
        
        # Format results
        results = []
        for i, pin in enumerate(top):
            results.append({
                'rank': i + 1,
                'id': pin.get('id'),
                'title': pin.get('title', 'Untitled')[:50],
                'description': (pin.get('description', '') or '')[:100],
                'link': pin.get('link', ''),
                'created_at': pin.get('created_at'),
                'board_id': pin.get('board_id'),
            })
        
        return {
            'total_analyzed': len(pins),
            'limit': limit,
            'sort_by': sort_by,
            'days_filter': days,
            'pins': results,
        }
    
    def get_top_by_board(self, limit: int = 10) -> Dict[str, Any]:
        """Get top pins from each board"""
        pins = self.bulk.get_all_pins()
        boards = self.analytics.get_boards()
        
        if not pins or not boards:
            return {'error': 'No data available'}
        
        # Group pins by board
        by_board = {}
        for pin in pins:
            board_id = pin.get('board_id')
            if board_id:
                if board_id not in by_board:
                    by_board[board_id] = []
                by_board[board_id].append(pin)
        
        # Get board names
        board_names = {b.get('id'): b.get('name', 'Unknown') for b in boards}
        
        # Get top pin from each board
        results = []
        for board_id, board_pins in by_board.items():
            if board_pins:
                # Sort by date (newest first)
                sorted_pins = sorted(board_pins, key=lambda x: x.get('created_at', ''), reverse=True)
                top_pin = sorted_pins[0]
                
                results.append({
                    'board_id': board_id,
                    'board_name': board_names.get(board_id, 'Unknown'),
                    'total_pins': len(board_pins),
                    'top_pin': {
                        'id': top_pin.get('id'),
                        'title': top_pin.get('title', 'Untitled')[:50],
                        'created_at': top_pin.get('created_at'),
                    }
                })
        
        # Sort by total pins
        results = sorted(results, key=lambda x: x['total_pins'], reverse=True)[:limit]
        
        return {
            'boards_analyzed': len(by_board),
            'results': results,
        }
    
    def get_newest_pins(self, limit: int = 10) -> List[Dict]:
        """Get newest pins"""
        return self.get_top_pins(limit=limit, sort_by='date')
    
    def get_pins_summary(self) -> Dict[str, Any]:
        """Get overall pins summary"""
        pins = self.bulk.get_all_pins()
        
        if not pins:
            return {'error': 'No pins found'}
        
        # Count by board
        by_board = {}
        for pin in pins:
            board = pin.get('board_id', 'Unknown')
            by_board[board] = by_board.get(board, 0) + 1
        
        # Find date range
        dates = []
        for pin in pins:
            created = pin.get('created_at')
            if created:
                try:
                    if isinstance(created, str):
                        dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                    else:
                        dt = created
                    dates.append(dt)
                except:
                    pass
        
        return {
            'total_pins': len(pins),
            'boards_used': len(by_board),
            'date_range': {
                'oldest': min(dates).isoformat() if dates else None,
                'newest': max(dates).isoformat() if dates else None,
            },
            'avg_per_board': round(len(pins) / max(len(by_board), 1), 1),
        }


def get_period_compare() -> PeriodCompare:
    """Get PeriodCompare instance"""
    return PeriodCompare()


def get_top_pins() -> TopPins:
    """Get TopPins instance"""
    return TopPins()
