"""
Pinterest Analytics Module (Community SDK)
Fetches analytics data from Pinterest API using python-pinterest
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import json

from .auth import get_api


class PinterestAnalytics:
    """Pinterest Analytics Data Fetcher using community SDK"""
    
    def __init__(self):
        self.api = get_api()
        if not self.api:
            raise RuntimeError("Pinterest API not configured. Run 'python main.py test' for setup instructions.")
        
    def get_user_account(self) -> Dict[str, Any]:
        """Get current user account information"""
        user = self.api.users.me()
        return {
            'id': getattr(user, 'id', None),
            'username': getattr(user, 'username', None),
            'account_type': getattr(user, 'account_type', None),
            'profile_image': getattr(user, 'profile_image', None),
            'website_url': getattr(user, 'website_url', None),
            'follower_count': getattr(user, 'follower_count', None),
            'following_count': getattr(user, 'following_count', None),
            'pin_count': getattr(user, 'pin_count', None),
            'board_count': getattr(user, 'board_count', None),
            'monthly_views': getattr(user, 'monthly_views', None),
        }
    
    def get_boards(self, page_size: int = 100) -> List[Dict[str, Any]]:
        """Get all boards for current user"""
        boards_response = self.api.boards.list(page_size=page_size)
        boards = []
        
        for board in boards_response.items:
            boards.append({
                'id': getattr(board, 'id', None),
                'name': getattr(board, 'name', None),
                'description': getattr(board, 'description', None),
                'pin_count': getattr(board, 'pin_count', None),
                'follower_count': getattr(board, 'follower_count', None),
                'privacy': getattr(board, 'privacy', None),
                'created_at': getattr(board, 'created_at', None),
            })
            
        return boards
    
    def get_board_pins(self, board_id: str, page_size: int = 100) -> List[Dict[str, Any]]:
        """Get pins from a specific board"""
        pins_response = self.api.boards.list_pins(board_id=board_id, page_size=page_size)
        pins = []
        
        for pin in pins_response.items:
            pins.append(self._pin_to_dict(pin))
            
        return pins
    
    def get_pins(self, page_size: int = 100) -> List[Dict[str, Any]]:
        """Get user's pins"""
        pins_response = self.api.pins.list(page_size=page_size)
        pins = []
        
        for pin in pins_response.items:
            pins.append(self._pin_to_dict(pin))
            
        return pins
    
    def get_pin(self, pin_id: str) -> Dict[str, Any]:
        """Get specific pin by ID"""
        pin = self.api.pins.get(pin_id=pin_id)
        return self._pin_to_dict(pin)
    
    def _pin_to_dict(self, pin) -> Dict[str, Any]:
        """Convert Pin object to dictionary"""
        return {
            'id': getattr(pin, 'id', None),
            'title': getattr(pin, 'title', None),
            'description': getattr(pin, 'description', None),
            'link': getattr(pin, 'link', None),
            'created_at': getattr(pin, 'created_at', None),
            'board_id': getattr(pin, 'board_id', None),
            'dominant_color': getattr(pin, 'dominant_color', None),
            'alt_text': getattr(pin, 'alt_text', None),
            'media_type': getattr(getattr(pin, 'media', None), 'media_type', None) if hasattr(pin, 'media') else None,
        }
    
    def get_user_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        metric_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get user account analytics (requires Business Account)
        
        Note: This endpoint may not be available for all accounts
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        if not metric_types:
            metric_types = ['IMPRESSION', 'ENGAGEMENT', 'PIN_CLICK', 'OUTBOUND_CLICK', 'SAVE']
        
        try:
            analytics = self.api.users.analytics(
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                metric_types=metric_types,
            )
            return analytics
        except Exception as e:
            return {
                'error': str(e),
                'note': 'Analytics may require a Pinterest Business Account'
            }
    
    def get_pin_analytics(
        self,
        pin_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get analytics for a specific pin"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
            
        try:
            analytics = self.api.pins.analytics(
                pin_id=pin_id,
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                metric_types=['IMPRESSION', 'SAVE', 'PIN_CLICK', 'OUTBOUND_CLICK'],
            )
            return analytics
        except Exception as e:
            return {
                'error': str(e),
                'note': 'Pin analytics may require a Pinterest Business Account'
            }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get account summary with basic stats"""
        user = self.get_user_account()
        boards = self.get_boards()
        
        return {
            'account': user,
            'boards_count': len(boards),
            'total_pins': sum(b.get('pin_count', 0) or 0 for b in boards),
            'total_followers': sum(b.get('follower_count', 0) or 0 for b in boards),
            'boards': boards,
        }


def get_analytics() -> PinterestAnalytics:
    """Get Pinterest Analytics instance"""
    return PinterestAnalytics()


if __name__ == '__main__':
    # Test analytics
    try:
        analytics = get_analytics()
        print("Fetching user account...")
        user = analytics.get_user_account()
        print(json.dumps(user, indent=2, default=str))
    except Exception as e:
        print(f"Error: {e}")
