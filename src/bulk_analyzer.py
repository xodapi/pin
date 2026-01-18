"""
Pinterest Bulk Analyzer
Analyze pins in bulk to find underperforming content
"""

import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

from .analytics import get_analytics


class BulkAnalyzer:
    """Analyze pins in bulk for cleanup and optimization"""
    
    def __init__(self):
        self.analytics = get_analytics()
        self._pins_cache = None
        self._boards_cache = None
        
    def get_all_pins(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """Get all pins from all boards"""
        if use_cache and self._pins_cache:
            return self._pins_cache
            
        print("Fetching all pins (this may take a while)...")
        
        all_pins = []
        boards = self.get_all_boards()
        
        for i, board in enumerate(boards):
            board_id = board.get('id')
            board_name = board.get('name', 'Unknown')
            
            print(f"  [{i+1}/{len(boards)}] {board_name}...", end=' ')
            
            try:
                pins = self.analytics.get_board_pins(board_id, page_size=250)
                for pin in pins:
                    pin['board_name'] = board_name
                    pin['board_id'] = board_id
                all_pins.extend(pins)
                print(f"{len(pins)} pins")
            except Exception as e:
                print(f"Error: {e}")
                
        self._pins_cache = all_pins
        print(f"\nTotal: {len(all_pins)} pins")
        return all_pins
    
    def get_all_boards(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """Get all boards"""
        if use_cache and self._boards_cache:
            return self._boards_cache
            
        self._boards_cache = self.analytics.get_boards()
        return self._boards_cache
    
    def find_underperforming(
        self, 
        min_saves: int = 1000,
        days: int = 180,
        metric: str = 'created_at'
    ) -> Dict[str, Any]:
        """
        Find underperforming pins
        
        Note: Since Pinterest API may not provide saves count directly,
        we analyze based on available metrics and age.
        
        Args:
            min_saves: Minimum saves threshold (if available)
            days: Only consider pins older than this many days
            metric: How to evaluate ('created_at', 'engagement')
        
        Returns:
            Analysis results with underperforming pins
        """
        all_pins = self.get_all_pins()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Categorize pins
        old_pins = []
        new_pins = []
        no_date_pins = []
        
        for pin in all_pins:
            created_at = pin.get('created_at')
            
            if not created_at:
                no_date_pins.append(pin)
                continue
                
            try:
                # Parse date (format may vary)
                if isinstance(created_at, str):
                    # Try different formats
                    for fmt in ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d']:
                        try:
                            pin_date = datetime.strptime(created_at[:19], fmt)
                            break
                        except:
                            continue
                    else:
                        no_date_pins.append(pin)
                        continue
                else:
                    pin_date = created_at
                    
                if pin_date < cutoff_date:
                    old_pins.append({
                        **pin,
                        'age_days': (datetime.now() - pin_date).days
                    })
                else:
                    new_pins.append(pin)
                    
            except Exception:
                no_date_pins.append(pin)
        
        # Sort old pins by age (oldest first)
        old_pins.sort(key=lambda x: x.get('age_days', 0), reverse=True)
        
        # Group by board
        pins_by_board = {}
        for pin in old_pins:
            board_name = pin.get('board_name', 'Unknown')
            if board_name not in pins_by_board:
                pins_by_board[board_name] = []
            pins_by_board[board_name].append(pin)
        
        return {
            'criteria': {
                'min_saves': min_saves,
                'older_than_days': days,
                'cutoff_date': cutoff_date.strftime('%Y-%m-%d'),
            },
            'summary': {
                'total_pins': len(all_pins),
                'old_pins': len(old_pins),
                'new_pins': len(new_pins),
                'no_date': len(no_date_pins),
                'percentage_old': round(len(old_pins) / max(len(all_pins), 1) * 100, 1),
            },
            'by_board': {
                board: len(pins) for board, pins in pins_by_board.items()
            },
            'pins': old_pins,
            'note': 'Pinterest API may not provide saves metric. Analysis based on age only.'
        }
    
    def find_top_performers(self, limit: int = 50) -> Dict[str, Any]:
        """Find best performing pins"""
        all_pins = self.get_all_pins()
        
        # Without engagement data, we can only show metadata
        # Once we have API access, we can enhance this
        
        # For now, show newest pins (most likely to have recent engagement)
        pins_with_date = []
        for pin in all_pins:
            created_at = pin.get('created_at')
            if created_at:
                pins_with_date.append(pin)
        
        # Sort by date (newest first)
        pins_with_date.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return {
            'total_analyzed': len(all_pins),
            'top_pins': pins_with_date[:limit],
            'note': 'Sorted by date. Engagement data requires Business account.'
        }
    
    def get_distribution(self) -> Dict[str, Any]:
        """Get pin distribution across boards"""
        boards = self.get_all_boards()
        
        # Sort by pin count
        sorted_boards = sorted(boards, key=lambda x: x.get('pin_count', 0) or 0, reverse=True)
        
        total_pins = sum(b.get('pin_count', 0) or 0 for b in boards)
        total_followers = sum(b.get('follower_count', 0) or 0 for b in boards)
        
        return {
            'total_boards': len(boards),
            'total_pins': total_pins,
            'total_board_followers': total_followers,
            'distribution': [
                {
                    'name': b.get('name'),
                    'pins': b.get('pin_count', 0) or 0,
                    'followers': b.get('follower_count', 0) or 0,
                    'percentage': round((b.get('pin_count', 0) or 0) / max(total_pins, 1) * 100, 1),
                }
                for b in sorted_boards
            ],
            'top_5': sorted_boards[:5],
            'empty_boards': [b for b in boards if (b.get('pin_count', 0) or 0) == 0],
        }
    
    def export_cleanup_list(
        self, 
        pins: List[Dict],
        filepath: Optional[Path] = None,
        format: str = 'json'
    ) -> Path:
        """Export list of pins to cleanup"""
        if not filepath:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = Path('reports') / f'cleanup_{timestamp}.{format}'
            
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        if format == 'json':
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(pins, f, indent=2, ensure_ascii=False, default=str)
        elif format == 'csv':
            import pandas as pd
            df = pd.DataFrame([{
                'id': p.get('id'),
                'title': p.get('title', '')[:50],
                'board': p.get('board_name'),
                'created_at': p.get('created_at'),
                'age_days': p.get('age_days'),
                'link': f"https://pinterest.com/pin/{p.get('id')}"
            } for p in pins])
            df.to_csv(filepath, index=False)
        elif format == 'txt':
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Cleanup list - {len(pins)} pins\n")
                f.write(f"Generated: {datetime.now()}\n")
                f.write("="*60 + "\n\n")
                for pin in pins:
                    f.write(f"ID: {pin.get('id')}\n")
                    f.write(f"Title: {pin.get('title', 'No title')}\n")
                    f.write(f"Board: {pin.get('board_name')}\n")
                    f.write(f"Age: {pin.get('age_days', '?')} days\n")
                    f.write(f"Link: https://pinterest.com/pin/{pin.get('id')}\n")
                    f.write("-"*40 + "\n")
                    
        return filepath


def get_bulk_analyzer() -> BulkAnalyzer:
    """Get BulkAnalyzer instance"""
    return BulkAnalyzer()


if __name__ == '__main__':
    analyzer = get_bulk_analyzer()
    result = analyzer.find_underperforming(min_saves=1000, days=180)
    print(json.dumps(result['summary'], indent=2))
