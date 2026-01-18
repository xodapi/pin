"""
Pinterest Mathematical Analytics
Advanced metrics and calculations for data-driven decisions
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict
import math

from .analytics import get_analytics
from .bulk_analyzer import get_bulk_analyzer


class MathAnalytics:
    """Mathematical analysis for Pinterest metrics"""
    
    def __init__(self):
        self.analytics = get_analytics()
        self.bulk = get_bulk_analyzer()
    
    def calculate_engagement_rate(self, impressions: int, engagements: int) -> float:
        """
        Calculate engagement rate
        Formula: (engagements / impressions) * 100
        
        Args:
            impressions: Total impressions
            engagements: Total engagements (saves + clicks + closeups)
            
        Returns:
            Engagement rate as percentage
        """
        if impressions <= 0:
            return 0.0
        return round((engagements / impressions) * 100, 2)
    
    def calculate_ctr(self, impressions: int, clicks: int) -> float:
        """
        Calculate Click-Through Rate
        Formula: (clicks / impressions) * 100
        
        Args:
            impressions: Total impressions
            clicks: Outbound clicks
            
        Returns:
            CTR as percentage
        """
        if impressions <= 0:
            return 0.0
        return round((clicks / impressions) * 100, 2)
    
    def calculate_save_rate(self, impressions: int, saves: int) -> float:
        """
        Calculate Save Rate
        Formula: (saves / impressions) * 100
        
        Args:
            impressions: Total impressions
            saves: Total saves
            
        Returns:
            Save rate as percentage
        """
        if impressions <= 0:
            return 0.0
        return round((saves / impressions) * 100, 2)
    
    def calculate_virality_score(self, saves: int, followers: int) -> float:
        """
        Calculate Virality Score - how much content spreads beyond followers
        Formula: (saves / followers) * 100
        
        Args:
            saves: Total saves
            followers: Account followers
            
        Returns:
            Virality score
        """
        if followers <= 0:
            return 0.0
        return round((saves / followers) * 100, 2)
    
    def calculate_growth_rate(
        self, 
        current_value: int, 
        previous_value: int
    ) -> float:
        """
        Calculate percentage growth rate
        Formula: ((current - previous) / previous) * 100
        
        Args:
            current_value: Current metric value
            previous_value: Previous period value
            
        Returns:
            Growth rate as percentage
        """
        if previous_value <= 0:
            if current_value > 0:
                return 100.0  # Infinite growth from zero
            return 0.0
        return round(((current_value - previous_value) / previous_value) * 100, 2)
    
    def calculate_efficiency_score(
        self,
        pins: int,
        followers: int,
        impressions: int = 0
    ) -> Dict[str, float]:
        """
        Calculate content efficiency metrics
        
        Args:
            pins: Total pins
            followers: Board/account followers
            impressions: Total impressions
            
        Returns:
            Dictionary with efficiency metrics
        """
        return {
            'followers_per_pin': round(followers / max(pins, 1), 2),
            'impressions_per_pin': round(impressions / max(pins, 1), 2) if impressions else 0,
            'pins_efficiency': 'High' if followers / max(pins, 1) > 1 else 'Medium' if followers / max(pins, 1) > 0.5 else 'Low',
        }
    
    def analyze_boards_math(self) -> Dict[str, Any]:
        """
        Mathematical analysis of all boards
        
        Returns:
            Comprehensive board analytics
        """
        boards = self.analytics.get_boards()
        
        if not boards:
            return {'error': 'No boards found'}
        
        # Calculate metrics for each board
        board_metrics = []
        total_pins = 0
        total_followers = 0
        
        for board in boards:
            pins = board.get('pin_count', 0) or 0
            followers = board.get('follower_count', 0) or 0
            
            total_pins += pins
            total_followers += followers
            
            efficiency = self.calculate_efficiency_score(pins, followers)
            
            board_metrics.append({
                'name': board.get('name', 'Unknown'),
                'id': board.get('id'),
                'pins': pins,
                'followers': followers,
                'efficiency': efficiency['followers_per_pin'],
                'efficiency_rating': efficiency['pins_efficiency'],
                'share_of_pins': 0,  # Will calculate after total
                'share_of_followers': 0,
            })
        
        # Calculate shares
        for bm in board_metrics:
            bm['share_of_pins'] = round(bm['pins'] / max(total_pins, 1) * 100, 1)
            bm['share_of_followers'] = round(bm['followers'] / max(total_followers, 1) * 100, 1)
        
        # Statistical analysis
        efficiencies = [b['efficiency'] for b in board_metrics if b['efficiency'] > 0]
        
        stats = {
            'total_boards': len(boards),
            'total_pins': total_pins,
            'total_followers': total_followers,
            'avg_pins_per_board': round(total_pins / max(len(boards), 1), 1),
            'avg_followers_per_board': round(total_followers / max(len(boards), 1), 1),
        }
        
        if efficiencies:
            stats['avg_efficiency'] = round(sum(efficiencies) / len(efficiencies), 2)
            stats['max_efficiency'] = round(max(efficiencies), 2)
            stats['min_efficiency'] = round(min(efficiencies), 2)
            
            # Standard deviation
            mean_eff = stats['avg_efficiency']
            variance = sum((e - mean_eff) ** 2 for e in efficiencies) / len(efficiencies)
            stats['std_deviation'] = round(math.sqrt(variance), 2)
        
        # Sort by efficiency
        top_efficient = sorted(board_metrics, key=lambda x: x['efficiency'], reverse=True)[:5]
        low_efficient = sorted(board_metrics, key=lambda x: x['efficiency'])[:5]
        
        # Recommendations based on math
        recommendations = []
        
        if stats.get('std_deviation', 0) > 2:
            recommendations.append("High variance in board efficiency - consider focusing on top performers")
        
        # Find underperformers (below avg - 1 std)
        if efficiencies:
            threshold = stats['avg_efficiency'] - stats.get('std_deviation', 0)
            underperformers = [b for b in board_metrics if b['efficiency'] < threshold]
            if underperformers:
                recommendations.append(f"{len(underperformers)} boards below average efficiency - consider consolidating")
        
        # Find boards with many pins but few followers
        for b in board_metrics:
            if b['pins'] > 100 and b['efficiency'] < 0.1:
                recommendations.append(f"'{b['name']}' has {b['pins']} pins but low engagement - needs optimization")
                break
        
        return {
            'boards': board_metrics,
            'statistics': stats,
            'top_efficient': top_efficient,
            'low_efficient': low_efficient,
            'recommendations': recommendations,
        }
    
    def analyze_pins_math(self, days: int = 30) -> Dict[str, Any]:
        """
        Mathematical analysis of pins over time
        
        Args:
            days: Analysis period in days
            
        Returns:
            Pin analytics with trends
        """
        pins = self.bulk.get_all_pins()
        
        if not pins:
            return {'error': 'No pins found'}
        
        # Parse dates and group by period
        now = datetime.now()
        cutoff = now - timedelta(days=days)
        
        by_week = defaultdict(int)
        by_month = defaultdict(int)
        by_day_of_week = defaultdict(int)
        by_hour = defaultdict(int)
        
        recent_pins = 0
        old_pins = 0
        
        for pin in pins:
            created = pin.get('created_at')
            if created:
                try:
                    if isinstance(created, str):
                        # Parse ISO format
                        dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                    else:
                        dt = created
                    
                    # Check if recent
                    if dt.replace(tzinfo=None) > cutoff:
                        recent_pins += 1
                    else:
                        old_pins += 1
                    
                    # Group by week
                    week_key = dt.strftime('%Y-W%W')
                    by_week[week_key] += 1
                    
                    # Group by month
                    month_key = dt.strftime('%Y-%m')
                    by_month[month_key] += 1
                    
                    # Day of week
                    by_day_of_week[dt.strftime('%A')] += 1
                    
                    # Hour
                    by_hour[dt.hour] += 1
                    
                except:
                    pass
        
        # Calculate posting frequency
        total_days = (now - min_date).days if 'min_date' in dir() else days
        
        # Find optimal posting times
        best_days = sorted(by_day_of_week.items(), key=lambda x: x[1], reverse=True)[:3]
        best_hours = sorted(by_hour.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Calculate activity score
        posts_per_day = len(pins) / max(total_days, 1)
        activity_rating = 'High' if posts_per_day >= 5 else 'Medium' if posts_per_day >= 1 else 'Low'
        
        # Trend analysis (last 4 weeks vs previous 4 weeks)
        weeks = sorted(by_week.keys(), reverse=True)
        recent_4_weeks = sum(by_week.get(w, 0) for w in weeks[:4])
        previous_4_weeks = sum(by_week.get(w, 0) for w in weeks[4:8])
        
        trend = 'Growing' if recent_4_weeks > previous_4_weeks else 'Declining' if recent_4_weeks < previous_4_weeks else 'Stable'
        trend_change = self.calculate_growth_rate(recent_4_weeks, previous_4_weeks)
        
        return {
            'total_pins': len(pins),
            'recent_pins': recent_pins,
            'old_pins': old_pins,
            'recency_ratio': round(recent_pins / max(len(pins), 1) * 100, 1),
            'posts_per_day': round(posts_per_day, 2),
            'activity_rating': activity_rating,
            'best_days': [{'day': d, 'count': c} for d, c in best_days],
            'best_hours': [{'hour': h, 'count': c} for h, c in best_hours],
            'by_week': dict(sorted(by_week.items())[-8:]),  # Last 8 weeks
            'by_month': dict(sorted(by_month.items())[-6:]),  # Last 6 months
            'trend': trend,
            'trend_change_percent': trend_change,
            'recommendations': self._generate_pin_recommendations(posts_per_day, trend_change),
        }
    
    def _generate_pin_recommendations(self, posts_per_day: float, trend_change: float) -> List[str]:
        """Generate recommendations based on pin analysis"""
        recs = []
        
        if posts_per_day < 1:
            recs.append("Increase posting frequency to at least 3-5 pins per day for better visibility")
        elif posts_per_day > 25:
            recs.append("High volume posting - ensure quality over quantity")
        
        if trend_change < -20:
            recs.append("Significant decrease in activity - consider resuming regular posting")
        elif trend_change > 50:
            recs.append("Great growth! Maintain this momentum")
        
        return recs
    
    def generate_health_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive account health report with scores
        
        Returns:
            Health report with overall score
        """
        try:
            summary = self.analytics.get_summary()
            boards = self.analytics.get_boards()
        except:
            return {'error': 'Failed to fetch data'}
        
        account = summary.get('account', {})
        
        # Calculate individual scores (0-100)
        scores = {}
        
        # Board score
        boards_count = len(boards)
        if boards_count >= 10:
            scores['boards'] = 100
        elif boards_count >= 5:
            scores['boards'] = 70
        elif boards_count >= 1:
            scores['boards'] = 40
        else:
            scores['boards'] = 0
        
        # Pins score
        total_pins = summary.get('total_pins', 0)
        if total_pins >= 500:
            scores['pins'] = 100
        elif total_pins >= 100:
            scores['pins'] = 70
        elif total_pins >= 20:
            scores['pins'] = 40
        else:
            scores['pins'] = 20
        
        # Followers score
        followers = account.get('follower_count', 0) or 0
        if followers >= 1000:
            scores['followers'] = 100
        elif followers >= 100:
            scores['followers'] = 60
        elif followers >= 10:
            scores['followers'] = 30
        else:
            scores['followers'] = 10
        
        # Efficiency score
        avg_efficiency = sum(b.get('follower_count', 0) or 0 for b in boards) / max(total_pins, 1)
        if avg_efficiency >= 1:
            scores['efficiency'] = 100
        elif avg_efficiency >= 0.5:
            scores['efficiency'] = 70
        elif avg_efficiency >= 0.1:
            scores['efficiency'] = 40
        else:
            scores['efficiency'] = 20
        
        # Calculate overall score (weighted average)
        weights = {'pins': 0.25, 'boards': 0.15, 'followers': 0.35, 'efficiency': 0.25}
        overall = sum(scores[k] * weights[k] for k in scores)
        
        # Rating
        if overall >= 80:
            rating = 'Excellent'
            emoji = '🏆'
        elif overall >= 60:
            rating = 'Good'
            emoji = '✅'
        elif overall >= 40:
            rating = 'Average'
            emoji = '⚠️'
        else:
            rating = 'Needs Work'
            emoji = '🔧'
        
        return {
            'overall_score': round(overall, 1),
            'rating': rating,
            'emoji': emoji,
            'scores': scores,
            'metrics': {
                'total_pins': total_pins,
                'boards': boards_count,
                'followers': followers,
                'avg_efficiency': round(avg_efficiency, 2),
            },
            'grade': self._score_to_grade(overall),
        }
    
    def _score_to_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return 'A+'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'B'
        elif score >= 60:
            return 'C'
        elif score >= 50:
            return 'D'
        else:
            return 'F'


def get_math_analytics() -> MathAnalytics:
    """Get MathAnalytics instance"""
    return MathAnalytics()
