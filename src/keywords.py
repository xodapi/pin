"""
Pinterest Keyword Analyzer
Analyze keywords for Pinterest SEO optimization
"""

import re
from collections import Counter
from typing import Dict, Any, List, Optional

from .analytics import get_analytics
from .bulk_analyzer import get_bulk_analyzer


class KeywordAnalyzer:
    """Analyze keywords for Pinterest SEO"""
    
    # Common stop words to filter out
    STOP_WORDS = {
        # English
        'the', 'and', 'for', 'with', 'this', 'that', 'from', 'are', 'was', 
        'you', 'your', 'will', 'can', 'all', 'has', 'have', 'been', 'were',
        'they', 'their', 'what', 'when', 'where', 'who', 'which', 'how',
        'not', 'but', 'just', 'also', 'more', 'some', 'any', 'only',
        'into', 'over', 'such', 'than', 'then', 'these', 'those',
        'about', 'after', 'before', 'between', 'through', 'during',
        # Russian
        'для', 'как', 'это', 'что', 'при', 'все', 'или', 'так', 'его', 
        'она', 'они', 'вам', 'вас', 'нас', 'наш', 'ваш', 'еще', 'уже',
        'был', 'была', 'были', 'быть', 'есть', 'нет', 'без', 'под',
        'над', 'при', 'про', 'между', 'через', 'после', 'перед',
        # Pinterest common
        'pin', 'pins', 'board', 'boards', 'save', 'saved', 'idea', 'ideas',
    }
    
    def __init__(self):
        self.analytics = get_analytics()
        self.bulk = get_bulk_analyzer()
        
    def analyze_my_keywords(self, min_count: int = 2) -> Dict[str, Any]:
        """
        Analyze keywords used in your own pins
        
        Args:
            min_count: Minimum occurrences to include
            
        Returns:
            Keyword analysis results
        """
        pins = self.bulk.get_all_pins()
        
        if not pins:
            return {'error': 'No pins found'}
        
        # Extract text from pins
        all_words = []
        title_words = []
        description_words = []
        
        for pin in pins:
            title = pin.get('title', '') or ''
            description = pin.get('description', '') or ''
            
            # Extract words
            t_words = self._extract_words(title)
            d_words = self._extract_words(description)
            
            title_words.extend(t_words)
            description_words.extend(d_words)
            all_words.extend(t_words + d_words)
        
        # Count occurrences
        all_counts = Counter(all_words)
        title_counts = Counter(title_words)
        
        # Filter by min count and remove stop words
        filtered = {
            word: count for word, count in all_counts.items()
            if count >= min_count and len(word) >= 3
        }
        
        # Sort by frequency
        sorted_keywords = sorted(filtered.items(), key=lambda x: x[1], reverse=True)
        
        # Analyze keyword types
        keyword_types = self._categorize_keywords([kw for kw, _ in sorted_keywords[:50]])
        
        return {
            'total_pins_analyzed': len(pins),
            'total_words': len(all_words),
            'unique_keywords': len(filtered),
            'top_keywords': [
                {'keyword': kw, 'count': count, 'frequency': round(count / len(pins) * 100, 1)}
                for kw, count in sorted_keywords[:30]
            ],
            'title_keywords': [
                {'keyword': kw, 'count': count}
                for kw, count in title_counts.most_common(15)
                if kw not in self.STOP_WORDS and len(kw) >= 3
            ],
            'categories': keyword_types,
            'recommendations': self._generate_recommendations(sorted_keywords, pins),
        }
    
    def _extract_words(self, text: str) -> List[str]:
        """Extract meaningful words from text"""
        if not text:
            return []
        
        # Clean and split
        text = text.lower()
        words = re.findall(r'\b[a-zA-Zа-яА-Я]{3,}\b', text)
        
        # Filter stop words
        return [w for w in words if w not in self.STOP_WORDS]
    
    def _categorize_keywords(self, keywords: List[str]) -> Dict[str, List[str]]:
        """Categorize keywords by type"""
        categories = {
            'colors': [],
            'styles': [],
            'subjects': [],
            'actions': [],
            'other': [],
        }
        
        color_words = {'red', 'blue', 'green', 'black', 'white', 'pink', 'gold', 
                      'silver', 'yellow', 'purple', 'orange', 'brown', 'gray',
                      'красный', 'синий', 'зеленый', 'черный', 'белый'}
        
        style_words = {'modern', 'vintage', 'minimalist', 'rustic', 'bohemian',
                      'classic', 'elegant', 'cute', 'aesthetic', 'cozy',
                      'современный', 'винтажный', 'минималистичный'}
        
        action_words = {'diy', 'make', 'create', 'design', 'build', 'craft',
                       'tutorial', 'guide', 'tips', 'ideas', 'inspiration'}
        
        for kw in keywords:
            if kw in color_words:
                categories['colors'].append(kw)
            elif kw in style_words:
                categories['styles'].append(kw)
            elif kw in action_words:
                categories['actions'].append(kw)
            else:
                # Check if it's likely a subject/noun
                if len(kw) > 4:
                    categories['subjects'].append(kw)
                else:
                    categories['other'].append(kw)
        
        return {k: v for k, v in categories.items() if v}
    
    def _generate_recommendations(self, keywords: List, pins: List) -> List[str]:
        """Generate SEO recommendations"""
        recommendations = []
        
        if not keywords:
            recommendations.append("Add more keywords to your pin titles and descriptions")
            return recommendations
        
        # Check keyword diversity
        if len(keywords) < 20:
            recommendations.append("Expand your keyword variety - aim for 50+ different keywords")
        
        # Check top keywords
        top_kw = [kw for kw, _ in keywords[:5]]
        recommendations.append(f"Your top keywords: {', '.join(top_kw)}")
        
        # Check for long-tail keywords (multi-word)
        recommendations.append("Tip: Use long-tail keywords like 'easy DIY home decor' instead of just 'decor'")
        
        # Pinterest-specific tips
        recommendations.append("Pinterest SEO: Include keywords in first 100 characters of description")
        
        return recommendations
    
    def check_keyword(self, keyword: str) -> Dict[str, Any]:
        """
        Check how a specific keyword is used in your content
        
        Args:
            keyword: Keyword to check
            
        Returns:
            Keyword usage statistics
        """
        pins = self.bulk.get_all_pins()
        keyword_lower = keyword.lower()
        
        matching_pins = []
        in_title = 0
        in_description = 0
        
        for pin in pins:
            title = (pin.get('title', '') or '').lower()
            description = (pin.get('description', '') or '').lower()
            
            title_match = keyword_lower in title
            desc_match = keyword_lower in description
            
            if title_match or desc_match:
                matching_pins.append({
                    'id': pin.get('id'),
                    'title': pin.get('title', '')[:50],
                    'in_title': title_match,
                    'in_description': desc_match,
                })
                if title_match:
                    in_title += 1
                if desc_match:
                    in_description += 1
        
        coverage = len(matching_pins) / max(len(pins), 1) * 100
        
        return {
            'keyword': keyword,
            'total_pins': len(pins),
            'matching_pins': len(matching_pins),
            'coverage': round(coverage, 1),
            'in_title': in_title,
            'in_description': in_description,
            'pins': matching_pins[:10],
            'recommendation': self._keyword_recommendation(keyword, coverage, in_title),
        }
    
    def _keyword_recommendation(self, keyword: str, coverage: float, in_title: int) -> str:
        """Generate recommendation for a specific keyword"""
        if coverage > 30:
            return f"'{keyword}' is well-used in your content ({coverage:.0f}% coverage)"
        elif coverage > 10:
            return f"Consider using '{keyword}' more often for better SEO"
        elif coverage > 0:
            return f"'{keyword}' is rarely used - add it to more pins if relevant"
        else:
            return f"'{keyword}' not found in your content - start using it!"


def get_keyword_analyzer() -> KeywordAnalyzer:
    """Get KeywordAnalyzer instance"""
    return KeywordAnalyzer()


if __name__ == '__main__':
    import json
    analyzer = get_keyword_analyzer()
    result = analyzer.analyze_my_keywords()
    print(json.dumps(result, indent=2, ensure_ascii=False))
