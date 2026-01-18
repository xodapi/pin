"""
Pinterest Quick Report
Fast 30-second status check for busy users
"""

from datetime import datetime
from typing import Dict, Any

from .analytics import get_analytics
from .daily_report import get_daily_report


class QuickReport:
    """Generate quick status reports"""
    
    def __init__(self):
        self.analytics = get_analytics()
        self.daily = get_daily_report()
        
    def generate(self) -> Dict[str, Any]:
        """
        Generate a quick 30-second report
        
        Returns:
            Quick summary with key metrics and one recommendation
        """
        report = {
            'generated_at': datetime.now().isoformat(),
            'status': 'OK',
            'metrics': {},
            'changes': {},
            'recommendation': None,
            'alerts': [],
        }
        
        try:
            # Get current summary
            summary = self.analytics.get_summary()
            account = summary.get('account', {})
            
            # Key metrics
            report['metrics'] = {
                'username': account.get('username', 'Unknown'),
                'pins': summary.get('total_pins', 0),
                'boards': summary.get('boards_count', 0),
                'followers': account.get('follower_count', 0),
                'monthly_views': account.get('monthly_views', 0),
            }
            
            # Compare with yesterday if available
            yesterday = self.daily.get_yesterday()
            if yesterday:
                yesterday_metrics = yesterday.get('metrics', {})
                
                for key in ['pins', 'boards', 'followers']:
                    current = report['metrics'].get(key, 0) or 0
                    previous = yesterday_metrics.get(f'total_{key}' if key == 'pins' else key, 0) or 0
                    
                    if previous > 0:
                        change = current - previous
                        change_pct = (change / previous) * 100
                        report['changes'][key] = {
                            'change': change,
                            'percent': round(change_pct, 1),
                        }
            
            # Generate recommendation
            report['recommendation'] = self._generate_recommendation(report)
            
            # Check for alerts
            report['alerts'] = self._check_alerts(report)
            
            # Overall status
            if report['alerts']:
                report['status'] = 'WARNING'
            else:
                report['status'] = 'OK'
                
        except Exception as e:
            report['status'] = 'ERROR'
            report['error'] = str(e)
        
        return report
    
    def _generate_recommendation(self, report: Dict) -> str:
        """Generate one actionable recommendation"""
        changes = report.get('changes', {})
        metrics = report.get('metrics', {})
        
        # Check for drops
        for key in ['followers', 'pins']:
            if key in changes:
                change_pct = changes[key].get('percent', 0)
                if change_pct < -10:
                    return f"Warning: {key} dropped {abs(change_pct)}%. Check your recent content."
        
        # Check for growth
        for key in ['followers']:
            if key in changes:
                change_pct = changes[key].get('percent', 0)
                if change_pct > 5:
                    return f"Great! {key} grew {change_pct}%. Keep doing what you're doing!"
        
        # Default recommendations based on metrics
        pins = metrics.get('pins', 0)
        if pins == 0:
            return "Start by creating your first pins!"
        elif pins < 50:
            return "Tip: Aim for at least 50 pins to improve discoverability."
        elif pins < 200:
            return "Good progress! Consistency is key - try to post regularly."
        else:
            return "Strong profile! Consider analyzing which boards perform best."
    
    def _check_alerts(self, report: Dict) -> list:
        """Check for important alerts"""
        alerts = []
        changes = report.get('changes', {})
        
        # Significant drops
        for key, data in changes.items():
            if data.get('percent', 0) < -20:
                alerts.append({
                    'type': 'WARNING',
                    'message': f'{key} dropped {abs(data["percent"])}% since yesterday'
                })
        
        return alerts
    
    def format_cli(self, report: Dict) -> str:
        """Format report for CLI display"""
        lines = []
        
        status = report.get('status', 'UNKNOWN')
        status_icon = '[OK]' if status == 'OK' else '[!]' if status == 'WARNING' else '[X]'
        
        lines.append(f"\n{status_icon} Quick Status - {report['metrics'].get('username', 'Unknown')}")
        lines.append("-" * 40)
        
        # Metrics
        m = report.get('metrics', {})
        changes = report.get('changes', {})
        
        def format_change(key):
            if key in changes:
                c = changes[key]
                sign = '+' if c['percent'] > 0 else ''
                return f" ({sign}{c['percent']}%)"
            return ""
        
        lines.append(f"Pins:      {m.get('pins', 0):,}{format_change('pins')}")
        lines.append(f"Boards:    {m.get('boards', 0):,}{format_change('boards')}")
        lines.append(f"Followers: {m.get('followers', 0):,}{format_change('followers')}")
        lines.append(f"Views:     {m.get('monthly_views', 0):,}/month")
        
        # Recommendation
        if report.get('recommendation'):
            lines.append("")
            lines.append(f"> {report['recommendation']}")
        
        # Alerts
        if report.get('alerts'):
            lines.append("")
            for alert in report['alerts']:
                lines.append(f"[!] {alert.get('message')}")
        
        return "\n".join(lines)


def get_quick_report() -> QuickReport:
    """Get QuickReport instance"""
    return QuickReport()


if __name__ == '__main__':
    reporter = get_quick_report()
    report = reporter.generate()
    print(reporter.format_cli(report))
