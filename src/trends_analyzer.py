"""
Pinterest Trends Analyzer
Analyze trends and find what's working
"""

import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import Counter
import re

from .analytics import get_analytics
from .bulk_analyzer import get_bulk_analyzer


class TrendsAnalyzer:
    """Analyze trends and patterns in Pinterest content"""
    
    def __init__(self):
        self.analytics = get_analytics()
        self.bulk = get_bulk_analyzer()
        
    def analyze_boards_performance(self) -> Dict[str, Any]:
        """Analyze which boards perform best"""
        boards = self.bulk.get_all_boards()
        
        if not boards:
            return {'error': 'No boards found'}
        
        # Calculate metrics
        total_pins = sum(b.get('pin_count', 0) or 0 for b in boards)
        total_followers = sum(b.get('follower_count', 0) or 0 for b in boards)
        
        # Find best performers
        by_pins = sorted(boards, key=lambda x: x.get('pin_count', 0) or 0, reverse=True)
        by_followers = sorted(boards, key=lambda x: x.get('follower_count', 0) or 0, reverse=True)
        
        # Calculate efficiency (followers per pin)
        boards_with_efficiency = []
        for b in boards:
            pins = b.get('pin_count', 0) or 0
            followers = b.get('follower_count', 0) or 0
            if pins > 0:
                efficiency = followers / pins
                boards_with_efficiency.append({
                    **b,
                    'efficiency': round(efficiency, 2),
                    'pins': pins,
                    'followers': followers,
                })
        
        by_efficiency = sorted(boards_with_efficiency, key=lambda x: x['efficiency'], reverse=True)
        
        return {
            'summary': {
                'total_boards': len(boards),
                'total_pins': total_pins,
                'total_followers': total_followers,
                'avg_pins_per_board': round(total_pins / max(len(boards), 1), 1),
                'avg_followers_per_board': round(total_followers / max(len(boards), 1), 1),
            },
            'top_by_pins': [
                {'name': b.get('name'), 'pins': b.get('pin_count', 0)}
                for b in by_pins[:5]
            ],
            'top_by_followers': [
                {'name': b.get('name'), 'followers': b.get('follower_count', 0)}
                for b in by_followers[:5]
            ],
            'most_efficient': [
                {'name': b.get('name'), 'efficiency': b.get('efficiency'), 'pins': b.get('pins'), 'followers': b.get('followers')}
                for b in by_efficiency[:5]
            ],
            'recommendations': self._generate_board_recommendations(boards, by_efficiency)
        }
    
    def _generate_board_recommendations(self, boards: List, by_efficiency: List) -> List[str]:
        """Generate recommendations based on board analysis"""
        recommendations = []
        
        # Find empty boards
        empty = [b for b in boards if (b.get('pin_count', 0) or 0) == 0]
        if empty:
            recommendations.append(f"Consider removing {len(empty)} empty board(s)")
        
        # Find low-efficiency boards with many pins
        if by_efficiency:
            avg_efficiency = sum(b['efficiency'] for b in by_efficiency) / len(by_efficiency)
            low_eff = [b for b in by_efficiency if b['efficiency'] < avg_efficiency * 0.5 and b['pins'] > 10]
            if low_eff:
                board_names = [b.get('name') for b in low_eff[:3]]
                recommendations.append(f"Low engagement boards: {', '.join(board_names)}")
        
        # Find high performers
        if by_efficiency:
            top = by_efficiency[0]
            recommendations.append(f"Best niche: '{top.get('name')}' ({top.get('efficiency'):.1f} followers per pin)")
        
        return recommendations
    
    def analyze_posting_patterns(self) -> Dict[str, Any]:
        """Analyze when pins were created"""
        pins = self.bulk.get_all_pins()
        
        if not pins:
            return {'error': 'No pins found'}
        
        # Analyze by day of week and hour
        day_counts = Counter()
        hour_counts = Counter()
        month_counts = Counter()
        
        for pin in pins:
            created_at = pin.get('created_at')
            if not created_at:
                continue
                
            try:
                if isinstance(created_at, str):
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                else:
                    dt = created_at
                    
                day_counts[dt.strftime('%A')] += 1
                hour_counts[dt.hour] += 1
                month_counts[dt.strftime('%Y-%m')] += 1
            except:
                continue
        
        # Find best days/hours
        best_days = day_counts.most_common(3)
        best_hours = hour_counts.most_common(5)
        
        return {
            'total_analyzed': len(pins),
            'by_day': dict(day_counts),
            'by_hour': dict(hour_counts),
            'by_month': dict(sorted(month_counts.items())),
            'best_days': [{'day': d, 'count': c} for d, c in best_days],
            'best_hours': [{'hour': h, 'count': c} for h, c in best_hours],
            'recommendations': [
                f"Most active day: {best_days[0][0] if best_days else 'Unknown'}",
                f"Best posting hour: {best_hours[0][0] if best_hours else 'Unknown'}:00",
            ]
        }
    
    def analyze_content_keywords(self) -> Dict[str, Any]:
        """Analyze keywords in pin titles"""
        pins = self.bulk.get_all_pins()
        
        if not pins:
            return {'error': 'No pins found'}
        
        # Extract words from titles
        all_words = []
        for pin in pins:
            title = pin.get('title', '') or pin.get('description', '') or ''
            # Clean and split
            words = re.findall(r'\b[a-zA-Zа-яА-Я]{3,}\b', title.lower())
            all_words.extend(words)
        
        # Count words (filter common words)
        stopwords = {'the', 'and', 'for', 'with', 'this', 'that', 'from', 'are', 'was', 'you', 
                     'как', 'для', 'это', 'что', 'при', 'все', 'или', 'так', 'его', 'она'}
        word_counts = Counter(w for w in all_words if w not in stopwords)
        
        top_words = word_counts.most_common(30)
        
        return {
            'total_pins_analyzed': len(pins),
            'total_words': len(all_words),
            'unique_words': len(word_counts),
            'top_keywords': [{'word': w, 'count': c} for w, c in top_words],
            'potential_niches': [w for w, c in top_words[:10]],
        }
    
    def find_niche(self) -> Dict[str, Any]:
        """Find user's niche based on content analysis"""
        boards_analysis = self.analyze_boards_performance()
        keywords = self.analyze_content_keywords()
        
        # Combine insights
        niche_signals = []
        
        # From boards
        if 'most_efficient' in boards_analysis:
            for board in boards_analysis['most_efficient'][:3]:
                niche_signals.append({
                    'source': 'board',
                    'value': board.get('name'),
                    'strength': board.get('efficiency', 0),
                })
        
        # From keywords
        if 'top_keywords' in keywords:
            for kw in keywords['top_keywords'][:5]:
                niche_signals.append({
                    'source': 'keyword',
                    'value': kw.get('word'),
                    'strength': kw.get('count', 0),
                })
        
        return {
            'niche_signals': niche_signals,
            'top_board_niche': boards_analysis.get('most_efficient', [{}])[0].get('name') if boards_analysis.get('most_efficient') else None,
            'top_keywords': [kw.get('word') for kw in keywords.get('top_keywords', [])[:5]],
            'recommendation': self._generate_niche_recommendation(boards_analysis, keywords),
        }
    
    def _generate_niche_recommendation(self, boards: Dict, keywords: Dict) -> str:
        """Generate niche recommendation"""
        parts = []
        
        if boards.get('most_efficient'):
            top_board = boards['most_efficient'][0]
            parts.append(f"Your best performing category: '{top_board.get('name')}'")
        
        if keywords.get('top_keywords'):
            top_kws = [kw['word'] for kw in keywords['top_keywords'][:3]]
            parts.append(f"Focus keywords: {', '.join(top_kws)}")
        
        return ' | '.join(parts) if parts else 'Need more data for recommendations'
    
    def generate_trends_report(self) -> Dict[str, Any]:
        """Generate comprehensive trends report"""
        print("Analyzing trends...")
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'boards': self.analyze_boards_performance(),
            'posting_patterns': self.analyze_posting_patterns(),
            'keywords': self.analyze_content_keywords(),
            'niche': self.find_niche(),
        }
        
        return report


def get_trends_analyzer() -> TrendsAnalyzer:
    """Get TrendsAnalyzer instance"""
    return TrendsAnalyzer()


if __name__ == '__main__':
    analyzer = get_trends_analyzer()
    report = analyzer.generate_trends_report()
    print(json.dumps(report, indent=2, default=str))
