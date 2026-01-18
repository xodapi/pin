"""
Pinterest Daily Report & Automation
Automated evening checks and daily reports
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
import os

# History storage
HISTORY_DIR = Path(__file__).parent.parent / 'data' / 'history'


class DailyReport:
    """Generate and store daily reports for trend tracking"""
    
    def __init__(self):
        HISTORY_DIR.mkdir(parents=True, exist_ok=True)
        self.today = datetime.now().strftime('%Y-%m-%d')
        
    def get_history_file(self, date: str) -> Path:
        """Get path to history file for a date"""
        return HISTORY_DIR / f'{date}.json'
    
    def save_daily_snapshot(self, data: Dict[str, Any]) -> Path:
        """Save today's stats snapshot"""
        snapshot = {
            'date': self.today,
            'timestamp': datetime.now().isoformat(),
            'account': data.get('account', {}),
            'metrics': {
                'total_pins': data.get('total_pins', 0),
                'total_boards': data.get('boards_count', 0),
                'total_followers': data.get('total_followers', 0),
                'impressions': data.get('impressions', 0),
                'saves': data.get('saves', 0),
                'clicks': data.get('clicks', 0),
            },
            'top_pins': data.get('top_pins', [])[:10],
        }
        
        filepath = self.get_history_file(self.today)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(snapshot, f, indent=2, ensure_ascii=False, default=str)
            
        return filepath
    
    def load_snapshot(self, date: str) -> Optional[Dict[str, Any]]:
        """Load snapshot for a specific date"""
        filepath = self.get_history_file(date)
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def get_yesterday(self) -> Optional[Dict[str, Any]]:
        """Get yesterday's snapshot"""
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        return self.load_snapshot(yesterday)
    
    def get_week_ago(self) -> Optional[Dict[str, Any]]:
        """Get snapshot from 7 days ago"""
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        return self.load_snapshot(week_ago)
    
    def compare_periods(self, current: Dict, previous: Dict) -> Dict[str, Any]:
        """Compare two periods and calculate changes"""
        if not previous:
            return {'no_previous_data': True}
            
        current_metrics = current.get('metrics', {})
        previous_metrics = previous.get('metrics', {})
        
        comparison = {}
        for key in current_metrics:
            curr_val = current_metrics.get(key, 0) or 0
            prev_val = previous_metrics.get(key, 0) or 0
            
            if prev_val > 0:
                change_pct = ((curr_val - prev_val) / prev_val) * 100
            else:
                change_pct = 100 if curr_val > 0 else 0
                
            comparison[key] = {
                'current': curr_val,
                'previous': prev_val,
                'change': curr_val - prev_val,
                'change_percent': round(change_pct, 1),
            }
            
        return comparison
    
    def generate_evening_report(self, analytics) -> Dict[str, Any]:
        """Generate comprehensive evening report"""
        print("Generating evening report...")
        
        # Get current data
        try:
            summary = analytics.get_summary()
            current_data = {
                'account': summary.get('account', {}),
                'total_pins': summary.get('total_pins', 0),
                'boards_count': summary.get('boards_count', 0),
                'total_followers': summary.get('total_followers', 0),
            }
            
            # Try to get analytics (Business accounts only)
            try:
                analytics_data = analytics.get_user_analytics()
                if 'error' not in analytics_data:
                    current_data['impressions'] = analytics_data.get('IMPRESSION', 0)
                    current_data['saves'] = analytics_data.get('SAVE', 0)
                    current_data['clicks'] = analytics_data.get('PIN_CLICK', 0)
            except:
                pass
                
        except Exception as e:
            return {'error': str(e)}
        
        # Save snapshot
        self.save_daily_snapshot(current_data)
        
        # Get previous periods
        yesterday = self.get_yesterday()
        week_ago = self.get_week_ago()
        
        # Build report
        report = {
            'date': self.today,
            'generated_at': datetime.now().isoformat(),
            'current': current_data,
            'vs_yesterday': self.compare_periods({'metrics': current_data}, yesterday) if yesterday else None,
            'vs_week_ago': self.compare_periods({'metrics': current_data}, week_ago) if week_ago else None,
            'health_status': self._check_health(current_data, yesterday),
            'alerts': self._generate_alerts(current_data, yesterday),
        }
        
        return report
    
    def _check_health(self, current: Dict, yesterday: Optional[Dict]) -> Dict[str, Any]:
        """Check account health status"""
        status = {
            'overall': 'OK',
            'checks': []
        }
        
        # Check if account is accessible
        if current.get('account', {}).get('username'):
            status['checks'].append({'name': 'Account Access', 'status': 'OK'})
        else:
            status['checks'].append({'name': 'Account Access', 'status': 'ERROR'})
            status['overall'] = 'ERROR'
        
        # Check for sudden drops
        if yesterday:
            yesterday_metrics = yesterday.get('metrics', {})
            
            # Impressions drop > 50%
            curr_imp = current.get('impressions', 0) or 0
            prev_imp = yesterday_metrics.get('impressions', 0) or 0
            if prev_imp > 0 and curr_imp < prev_imp * 0.5:
                status['checks'].append({
                    'name': 'Impressions Drop',
                    'status': 'WARNING',
                    'message': f'Dropped {int((1 - curr_imp/prev_imp) * 100)}% vs yesterday'
                })
                status['overall'] = 'WARNING'
            else:
                status['checks'].append({'name': 'Impressions', 'status': 'OK'})
        
        return status
    
    def _generate_alerts(self, current: Dict, yesterday: Optional[Dict]) -> list:
        """Generate alerts for important changes"""
        alerts = []
        
        if not yesterday:
            alerts.append({
                'type': 'INFO',
                'message': 'First day of tracking - no comparison available'
            })
            return alerts
        
        yesterday_metrics = yesterday.get('metrics', {})
        
        # Check impressions
        curr_imp = current.get('impressions', 0) or 0
        prev_imp = yesterday_metrics.get('impressions', 0) or 0
        
        if prev_imp > 0:
            change = (curr_imp - prev_imp) / prev_imp * 100
            if change < -30:
                alerts.append({
                    'type': 'WARNING',
                    'message': f'Impressions dropped {abs(int(change))}% - check for algorithm changes'
                })
            elif change > 50:
                alerts.append({
                    'type': 'SUCCESS',
                    'message': f'Impressions up {int(change)}%! Something is working well'
                })
        
        return alerts


def get_daily_report() -> DailyReport:
    """Get DailyReport instance"""
    return DailyReport()


if __name__ == '__main__':
    from analytics import get_analytics
    
    reporter = get_daily_report()
    analytics = get_analytics()
    
    report = reporter.generate_evening_report(analytics)
    print(json.dumps(report, indent=2, ensure_ascii=False, default=str))
