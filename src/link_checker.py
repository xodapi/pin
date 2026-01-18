"""
Pinterest Link Checker
Find broken links in your pins
"""

import re
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed
import httpx

from .bulk_analyzer import get_bulk_analyzer


class LinkChecker:
    """Check links in pins for broken URLs"""
    
    def __init__(self):
        self.bulk = get_bulk_analyzer()
        
    def check_all_links(self, max_workers: int = 10, timeout: int = 10) -> Dict[str, Any]:
        """
        Check all links in pins
        
        Args:
            max_workers: Number of parallel requests
            timeout: Request timeout in seconds
            
        Returns:
            Results with broken and working links
        """
        pins = self.bulk.get_all_pins()
        
        if not pins:
            return {'error': 'No pins found'}
        
        # Extract unique links
        links = {}
        for pin in pins:
            link = pin.get('link')
            if link and link.startswith('http'):
                if link not in links:
                    links[link] = []
                links[link].append({
                    'id': pin.get('id'),
                    'title': pin.get('title', '')[:50],
                })
        
        print(f"Checking {len(links)} unique links...")
        
        results = {
            'total_pins': len(pins),
            'pins_with_links': sum(1 for p in pins if p.get('link')),
            'unique_links': len(links),
            'broken': [],
            'redirects': [],
            'slow': [],
            'working': 0,
            'errors': [],
        }
        
        # Check links in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self._check_link, url, timeout): url
                for url in links.keys()
            }
            
            checked = 0
            for future in as_completed(futures):
                url = futures[future]
                checked += 1
                
                if checked % 20 == 0:
                    print(f"  Progress: {checked}/{len(links)}")
                
                try:
                    status = future.result()
                    
                    if status['status'] == 'broken':
                        results['broken'].append({
                            'url': url,
                            'error': status.get('error'),
                            'status_code': status.get('status_code'),
                            'pins': links[url],
                        })
                    elif status['status'] == 'redirect':
                        results['redirects'].append({
                            'url': url,
                            'redirect_to': status.get('redirect_to'),
                            'pins': links[url],
                        })
                    elif status['status'] == 'slow':
                        results['slow'].append({
                            'url': url,
                            'response_time': status.get('response_time'),
                            'pins': links[url],
                        })
                    else:
                        results['working'] += 1
                        
                except Exception as e:
                    results['errors'].append({
                        'url': url,
                        'error': str(e),
                    })
        
        # Summary
        results['summary'] = {
            'broken_count': len(results['broken']),
            'redirect_count': len(results['redirects']),
            'slow_count': len(results['slow']),
            'working_count': results['working'],
            'health_score': round(results['working'] / max(len(links), 1) * 100, 1),
        }
        
        return results
    
    def _check_link(self, url: str, timeout: int = 10) -> Dict[str, Any]:
        """Check a single link"""
        try:
            start_time = __import__('time').time()
            
            response = httpx.head(
                url,
                timeout=timeout,
                follow_redirects=False,
                headers={'User-Agent': 'Mozilla/5.0 (compatible; PinterestAnalytics/1.0)'}
            )
            
            response_time = __import__('time').time() - start_time
            
            # Check for redirects
            if response.status_code in (301, 302, 303, 307, 308):
                return {
                    'status': 'redirect',
                    'status_code': response.status_code,
                    'redirect_to': response.headers.get('location', ''),
                }
            
            # Check for errors
            if response.status_code >= 400:
                return {
                    'status': 'broken',
                    'status_code': response.status_code,
                    'error': f'HTTP {response.status_code}',
                }
            
            # Check for slow responses
            if response_time > 5:
                return {
                    'status': 'slow',
                    'response_time': round(response_time, 2),
                }
            
            return {'status': 'ok'}
            
        except httpx.TimeoutException:
            return {
                'status': 'broken',
                'error': 'Timeout',
            }
        except Exception as e:
            return {
                'status': 'broken',
                'error': str(e),
            }
    
    def get_links_without_utm(self) -> List[Dict[str, Any]]:
        """Find links without UTM tracking parameters"""
        pins = self.bulk.get_all_pins()
        
        missing_utm = []
        for pin in pins:
            link = pin.get('link', '')
            if link and 'utm_' not in link.lower():
                missing_utm.append({
                    'id': pin.get('id'),
                    'title': pin.get('title', '')[:50],
                    'link': link[:100],
                })
        
        return missing_utm


def get_link_checker() -> LinkChecker:
    """Get LinkChecker instance"""
    return LinkChecker()
