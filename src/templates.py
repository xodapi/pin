"""
Pinterest Description Templates
Help users write better pin descriptions for SEO
"""

from typing import Dict, Any, List
import re


class DescriptionHelper:
    """Help generate optimized pin descriptions"""
    
    # Pinterest SEO best practices
    MAX_DESCRIPTION_LENGTH = 500
    OPTIMAL_LENGTH = 200
    MIN_KEYWORDS = 3
    
    TEMPLATES = {
        'product': {
            'name': 'Product Pin',
            'template': '{product_name} - {key_benefit}. {description}. Shop now for {category}! #{hashtag1} #{hashtag2}',
            'example': 'Handmade Leather Bag - Perfect for daily use. Crafted with premium materials. Shop now for accessories! #leather #handmade',
        },
        'recipe': {
            'name': 'Recipe Pin',
            'template': '{dish_name} Recipe - {cooking_time} | {difficulty}. {description}. Save this delicious {category} recipe! #{hashtag1} #{hashtag2}',
            'example': 'Chocolate Chip Cookies Recipe - 30 mins | Easy. Soft, chewy, and delicious! Save this dessert recipe! #baking #cookies',
        },
        'diy': {
            'name': 'DIY Project',
            'template': 'DIY {project_name} - {difficulty} | {time}. {description}. Try this {category} project! #{hashtag1} #{hashtag2}',
            'example': 'DIY Wall Art - Easy | 1 hour. Transform your space with this simple craft. Try this home decor project! #diy #homedecor',
        },
        'inspiration': {
            'name': 'Inspiration',
            'template': '{topic} Inspiration - {description}. Save for later! #{hashtag1} #{hashtag2} #{hashtag3}',
            'example': 'Wedding Decor Inspiration - Elegant rustic theme ideas for your special day. Save for later! #wedding #rustic #decor',
        },
        'tutorial': {
            'name': 'Tutorial',
            'template': 'How to {action} - Step by step guide. {description}. Learn more about {topic}! #{hashtag1} #{hashtag2}',
            'example': 'How to Draw Flowers - Step by step guide. Perfect for beginners! Learn drawing! #art #tutorial',
        },
        'quote': {
            'name': 'Quote',
            'template': '"{quote}" - {author}. {context}. #{hashtag1} #{hashtag2}',
            'example': '"The only way to do great work is to love what you do" - Steve Jobs. Daily motivation! #quotes #motivation',
        },
        'art': {
            'name': 'Art/Illustration',
            'template': '{title} - {style} {medium}. {description}. #{hashtag1} #{hashtag2} #{hashtag3}',
            'example': 'Sunset Mountains - Digital illustration. Capturing the beauty of nature. #art #digital #landscape',
        },
    }
    
    POPULAR_HASHTAGS = {
        'general': ['pinterest', 'inspo', 'aesthetic', 'ideas', 'trending'],
        'home': ['homedecor', 'interiordesign', 'homedesign', 'decor', 'home'],
        'food': ['recipe', 'food', 'cooking', 'yummy', 'foodie', 'homemade'],
        'fashion': ['fashion', 'style', 'outfit', 'ootd', 'streetstyle'],
        'art': ['art', 'artist', 'illustration', 'drawing', 'artwork', 'creative'],
        'diy': ['diy', 'crafts', 'handmade', 'doityourself', 'tutorial'],
        'beauty': ['beauty', 'makeup', 'skincare', 'beautytips', 'glam'],
        'travel': ['travel', 'wanderlust', 'adventure', 'explore', 'vacation'],
        'wedding': ['wedding', 'bride', 'weddingideas', 'weddinginspo', 'engaged'],
        'fitness': ['fitness', 'workout', 'health', 'gym', 'fitnessmotivation'],
    }
    
    def get_templates(self) -> List[Dict[str, Any]]:
        """Get all available templates"""
        return [
            {'key': key, **template}
            for key, template in self.TEMPLATES.items()
        ]
    
    def get_template(self, template_key: str) -> Dict[str, Any]:
        """Get a specific template"""
        return self.TEMPLATES.get(template_key, self.TEMPLATES['inspiration'])
    
    def analyze_description(self, description: str) -> Dict[str, Any]:
        """Analyze a description for SEO quality"""
        if not description:
            return {
                'score': 0,
                'issues': ['No description provided'],
                'suggestions': ['Add a description with keywords'],
            }
        
        issues = []
        suggestions = []
        score = 100
        
        # Length check
        length = len(description)
        if length < 50:
            issues.append('Too short (< 50 chars)')
            suggestions.append('Add more details to reach 100-200 characters')
            score -= 20
        elif length > self.MAX_DESCRIPTION_LENGTH:
            issues.append(f'Too long (> {self.MAX_DESCRIPTION_LENGTH} chars)')
            suggestions.append('Shorten to under 500 characters')
            score -= 10
        elif length < 100:
            suggestions.append('Consider adding more detail')
            score -= 5
        
        # Hashtag check
        hashtags = re.findall(r'#\w+', description)
        if len(hashtags) == 0:
            issues.append('No hashtags')
            suggestions.append('Add 2-5 relevant hashtags')
            score -= 15
        elif len(hashtags) > 10:
            issues.append('Too many hashtags')
            suggestions.append('Reduce to 5-8 hashtags')
            score -= 10
        
        # Call to action check
        cta_words = ['save', 'click', 'shop', 'try', 'learn', 'discover', 'get', 'find']
        has_cta = any(word in description.lower() for word in cta_words)
        if not has_cta:
            suggestions.append('Add a call-to-action (Save, Shop, Try, etc.)')
            score -= 10
        
        # Emoji check (optional)
        has_emoji = bool(re.search(r'[\U0001F300-\U0001F9FF]', description))
        if not has_emoji:
            suggestions.append('Consider adding an emoji for engagement')
        
        # Keywords in first 100 chars
        first_100 = description[:100].lower()
        is_keyword_rich = len(first_100.split()) >= 10
        if not is_keyword_rich:
            suggestions.append('Put important keywords in first 100 characters')
            score -= 5
        
        return {
            'score': max(0, score),
            'length': length,
            'hashtags': hashtags,
            'hashtag_count': len(hashtags),
            'has_cta': has_cta,
            'has_emoji': has_emoji,
            'issues': issues,
            'suggestions': suggestions,
            'rating': 'Excellent' if score >= 90 else 'Good' if score >= 70 else 'Needs improvement' if score >= 50 else 'Poor',
        }
    
    def suggest_hashtags(self, category: str, text: str = '') -> List[str]:
        """Suggest hashtags based on category and content"""
        suggested = []
        
        # Add category hashtags
        if category in self.POPULAR_HASHTAGS:
            suggested.extend(self.POPULAR_HASHTAGS[category][:5])
        
        # Add general hashtags
        suggested.extend(self.POPULAR_HASHTAGS['general'][:3])
        
        # Extract potential hashtags from text
        if text:
            words = re.findall(r'\b\w{4,15}\b', text.lower())
            common = ['this', 'that', 'with', 'from', 'have', 'your', 'about']
            words = [w for w in words if w not in common][:5]
            suggested.extend(words)
        
        # Remove duplicates while preserving order
        seen = set()
        unique = []
        for tag in suggested:
            if tag not in seen:
                seen.add(tag)
                unique.append(tag)
        
        return unique[:10]
    
    def generate_description(
        self,
        template_key: str,
        **kwargs
    ) -> str:
        """Generate a description from template"""
        template = self.TEMPLATES.get(template_key)
        if not template:
            return ''
        
        try:
            return template['template'].format(**kwargs)
        except KeyError as e:
            return f"Missing field: {e}"


def get_description_helper() -> DescriptionHelper:
    """Get DescriptionHelper instance"""
    return DescriptionHelper()
