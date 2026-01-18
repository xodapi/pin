"""
Pinterest Watchlist Manager
Create and manage custom collections of tracked pins and boards
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from .analytics import get_analytics
from .bulk_analyzer import get_bulk_analyzer


class WatchlistManager:
    """Manage custom watchlists of pins and boards"""
    
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path('data/watchlists')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.analytics = get_analytics()
        self.bulk = get_bulk_analyzer()
        
    def create_watchlist(self, name: str, description: str = "") -> Dict[str, Any]:
        """
        Create a new watchlist
        
        Args:
            name: Watchlist name (will be used as filename)
            description: Optional description
            
        Returns:
            Created watchlist data
        """
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_name = safe_name.replace(' ', '_').lower()
        
        watchlist = {
            'id': safe_name,
            'name': name,
            'description': description,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'pins': [],
            'boards': [],
            'snapshots': [],
        }
        
        self._save_watchlist(safe_name, watchlist)
        return watchlist
    
    def list_watchlists(self) -> List[Dict[str, Any]]:
        """List all watchlists"""
        watchlists = []
        
        for filepath in self.data_dir.glob('*.json'):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    watchlists.append({
                        'id': data.get('id', filepath.stem),
                        'name': data.get('name', filepath.stem),
                        'description': data.get('description', ''),
                        'pins_count': len(data.get('pins', [])),
                        'boards_count': len(data.get('boards', [])),
                        'created_at': data.get('created_at'),
                    })
            except:
                pass
        
        return watchlists
    
    def get_watchlist(self, watchlist_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific watchlist"""
        filepath = self.data_dir / f"{watchlist_id}.json"
        
        if not filepath.exists():
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def delete_watchlist(self, watchlist_id: str) -> bool:
        """Delete a watchlist"""
        filepath = self.data_dir / f"{watchlist_id}.json"
        
        if filepath.exists():
            filepath.unlink()
            return True
        return False
    
    def add_pin(self, watchlist_id: str, pin_id: str, note: str = "") -> Dict[str, Any]:
        """Add a pin to watchlist"""
        watchlist = self.get_watchlist(watchlist_id)
        
        if not watchlist:
            return {'error': f'Watchlist not found: {watchlist_id}'}
        
        # Check if already exists
        if any(p['id'] == pin_id for p in watchlist['pins']):
            return {'error': 'Pin already in watchlist'}
        
        watchlist['pins'].append({
            'id': pin_id,
            'note': note,
            'added_at': datetime.now().isoformat(),
        })
        
        watchlist['updated_at'] = datetime.now().isoformat()
        self._save_watchlist(watchlist_id, watchlist)
        
        return {'success': True, 'pins_count': len(watchlist['pins'])}
    
    def add_board(self, watchlist_id: str, board_id: str, note: str = "") -> Dict[str, Any]:
        """Add a board to watchlist"""
        watchlist = self.get_watchlist(watchlist_id)
        
        if not watchlist:
            return {'error': f'Watchlist not found: {watchlist_id}'}
        
        # Check if already exists
        if any(b['id'] == board_id for b in watchlist['boards']):
            return {'error': 'Board already in watchlist'}
        
        watchlist['boards'].append({
            'id': board_id,
            'note': note,
            'added_at': datetime.now().isoformat(),
        })
        
        watchlist['updated_at'] = datetime.now().isoformat()
        self._save_watchlist(watchlist_id, watchlist)
        
        return {'success': True, 'boards_count': len(watchlist['boards'])}
    
    def remove_pin(self, watchlist_id: str, pin_id: str) -> Dict[str, Any]:
        """Remove a pin from watchlist"""
        watchlist = self.get_watchlist(watchlist_id)
        
        if not watchlist:
            return {'error': f'Watchlist not found: {watchlist_id}'}
        
        original_count = len(watchlist['pins'])
        watchlist['pins'] = [p for p in watchlist['pins'] if p['id'] != pin_id]
        
        if len(watchlist['pins']) == original_count:
            return {'error': 'Pin not found in watchlist'}
        
        watchlist['updated_at'] = datetime.now().isoformat()
        self._save_watchlist(watchlist_id, watchlist)
        
        return {'success': True}
    
    def remove_board(self, watchlist_id: str, board_id: str) -> Dict[str, Any]:
        """Remove a board from watchlist"""
        watchlist = self.get_watchlist(watchlist_id)
        
        if not watchlist:
            return {'error': f'Watchlist not found: {watchlist_id}'}
        
        original_count = len(watchlist['boards'])
        watchlist['boards'] = [b for b in watchlist['boards'] if b['id'] != board_id]
        
        if len(watchlist['boards']) == original_count:
            return {'error': 'Board not found in watchlist'}
        
        watchlist['updated_at'] = datetime.now().isoformat()
        self._save_watchlist(watchlist_id, watchlist)
        
        return {'success': True}
    
    def take_snapshot(self, watchlist_id: str) -> Dict[str, Any]:
        """
        Take a snapshot of current metrics for watchlist items
        Useful for tracking progress over time
        """
        watchlist = self.get_watchlist(watchlist_id)
        
        if not watchlist:
            return {'error': f'Watchlist not found: {watchlist_id}'}
        
        # Get current data
        all_boards = self.analytics.get_boards()
        all_pins = self.bulk.get_all_pins()
        
        # Build lookup
        boards_map = {b.get('id'): b for b in all_boards}
        pins_map = {p.get('id'): p for p in all_pins}
        
        # Collect current metrics
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'pins': [],
            'boards': [],
        }
        
        for pin_ref in watchlist['pins']:
            pin_data = pins_map.get(pin_ref['id'])
            if pin_data:
                snapshot['pins'].append({
                    'id': pin_ref['id'],
                    'title': pin_data.get('title', '')[:50],
                    'link': pin_data.get('link'),
                })
        
        for board_ref in watchlist['boards']:
            board_data = boards_map.get(board_ref['id'])
            if board_data:
                snapshot['boards'].append({
                    'id': board_ref['id'],
                    'name': board_data.get('name'),
                    'pin_count': board_data.get('pin_count', 0),
                    'follower_count': board_data.get('follower_count', 0),
                })
        
        # Save snapshot
        watchlist['snapshots'].append(snapshot)
        
        # Keep only last 30 snapshots
        if len(watchlist['snapshots']) > 30:
            watchlist['snapshots'] = watchlist['snapshots'][-30:]
        
        watchlist['updated_at'] = datetime.now().isoformat()
        self._save_watchlist(watchlist_id, watchlist)
        
        return {'success': True, 'snapshot': snapshot}
    
    def get_analytics(self, watchlist_id: str) -> Dict[str, Any]:
        """
        Get analytics for a watchlist
        
        Args:
            watchlist_id: Watchlist ID
            
        Returns:
            Analytics data for tracked items
        """
        watchlist = self.get_watchlist(watchlist_id)
        
        if not watchlist:
            return {'error': f'Watchlist not found: {watchlist_id}'}
        
        # Get current data
        all_boards = self.analytics.get_boards()
        all_pins = self.bulk.get_all_pins()
        
        # Build lookup
        boards_map = {b.get('id'): b for b in all_boards}
        pins_map = {p.get('id'): p for p in all_pins}
        
        # Collect analytics
        pins_data = []
        for pin_ref in watchlist['pins']:
            pin = pins_map.get(pin_ref['id'])
            if pin:
                pins_data.append({
                    'id': pin_ref['id'],
                    'title': pin.get('title', 'Untitled')[:50],
                    'description': (pin.get('description', '') or '')[:100],
                    'link': pin.get('link'),
                    'created_at': pin.get('created_at'),
                    'board_id': pin.get('board_id'),
                    'note': pin_ref.get('note', ''),
                    'added_at': pin_ref.get('added_at'),
                })
        
        boards_data = []
        total_pins_tracked = 0
        total_followers_tracked = 0
        
        for board_ref in watchlist['boards']:
            board = boards_map.get(board_ref['id'])
            if board:
                pin_count = board.get('pin_count', 0) or 0
                follower_count = board.get('follower_count', 0) or 0
                
                total_pins_tracked += pin_count
                total_followers_tracked += follower_count
                
                boards_data.append({
                    'id': board_ref['id'],
                    'name': board.get('name', 'Unknown'),
                    'pin_count': pin_count,
                    'follower_count': follower_count,
                    'efficiency': round(follower_count / max(pin_count, 1), 2),
                    'privacy': board.get('privacy', 'PUBLIC'),
                    'note': board_ref.get('note', ''),
                    'added_at': board_ref.get('added_at'),
                })
        
        # Compare with last snapshot if available
        changes = {}
        if watchlist.get('snapshots') and len(watchlist['snapshots']) >= 2:
            last = watchlist['snapshots'][-1]
            prev = watchlist['snapshots'][-2]
            
            # Calculate board changes
            last_boards = {b['id']: b for b in last.get('boards', [])}
            prev_boards = {b['id']: b for b in prev.get('boards', [])}
            
            for board_id, last_board in last_boards.items():
                if board_id in prev_boards:
                    changes[board_id] = {
                        'pins': last_board.get('pin_count', 0) - prev_boards[board_id].get('pin_count', 0),
                        'followers': last_board.get('follower_count', 0) - prev_boards[board_id].get('follower_count', 0),
                    }
        
        return {
            'watchlist': {
                'id': watchlist['id'],
                'name': watchlist['name'],
                'description': watchlist.get('description', ''),
            },
            'summary': {
                'pins_tracked': len(pins_data),
                'boards_tracked': len(boards_data),
                'total_pins_in_boards': total_pins_tracked,
                'total_followers': total_followers_tracked,
                'snapshots_count': len(watchlist.get('snapshots', [])),
            },
            'pins': pins_data,
            'boards': boards_data,
            'changes': changes,
            'last_updated': watchlist.get('updated_at'),
        }
    
    def _save_watchlist(self, watchlist_id: str, data: Dict):
        """Save watchlist to file"""
        filepath = self.data_dir / f"{watchlist_id}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


def get_watchlist_manager(data_dir: Optional[Path] = None) -> WatchlistManager:
    """Get WatchlistManager instance"""
    return WatchlistManager(data_dir)
