"""
Pinterest Report Generator (Community SDK)
Generates reports in various formats
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

import pandas as pd

from .analytics import get_analytics


class ReportGenerator:
    """Generate reports from Pinterest data"""
    
    def __init__(self, output_dir: str = 'reports'):
        self.analytics = get_analytics()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def _get_filename(self, name: str, ext: str) -> Path:
        """Generate timestamped filename"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return self.output_dir / f'{name}_{timestamp}.{ext}'
    
    def _save_data(self, data: Any, name: str, format: str) -> Path:
        """Save data in specified format"""
        if format == 'json':
            filepath = self._get_filename(name, 'json')
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        elif format == 'excel':
            filepath = self._get_filename(name, 'xlsx')
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                df = pd.DataFrame([data])
            else:
                df = pd.DataFrame(data)
            df.to_excel(filepath, index=False, engine='openpyxl')
        else:  # csv
            filepath = self._get_filename(name, 'csv')
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                df = pd.DataFrame([data])
            else:
                df = pd.DataFrame(data)
            df.to_csv(filepath, index=False)
            
        return filepath
    
    def generate_summary_report(self, format: str = 'json') -> Path:
        """Generate account summary report"""
        print("📊 Fetching account summary...")
        summary = self.analytics.get_summary()
        
        if format == 'json':
            return self._save_data(summary, 'summary', 'json')
        else:
            # Flatten for tabular format
            account = summary['account']
            account['boards_count'] = summary['boards_count']
            account['total_pins'] = summary['total_pins']
            return self._save_data(account, 'summary', format)
    
    def generate_boards_report(self, format: str = 'json') -> Path:
        """Generate boards report"""
        print("📋 Fetching boards...")
        boards = self.analytics.get_boards()
        return self._save_data(boards, 'boards', format)
    
    def generate_pins_report(self, format: str = 'json', limit: int = 100) -> Path:
        """Generate pins report"""
        print(f"📌 Fetching pins (limit: {limit})...")
        pins = self.analytics.get_pins(page_size=limit)
        return self._save_data(pins, 'pins', format)
    
    def generate_full_report(self, format: str = 'json') -> Path:
        """Generate comprehensive report"""
        print("📊 Generating full report...")
        
        user = self.analytics.get_user_account()
        boards = self.analytics.get_boards()
        pins = self.analytics.get_pins(page_size=100)
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'account': user,
            'boards': boards,
            'pins': pins,
        }
        
        if format == 'json':
            return self._save_data(report, 'full_report', 'json')
        elif format == 'excel':
            filepath = self._get_filename('full_report', 'xlsx')
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                pd.DataFrame([user]).to_excel(writer, sheet_name='Account', index=False)
                pd.DataFrame(boards).to_excel(writer, sheet_name='Boards', index=False)
                pd.DataFrame(pins).to_excel(writer, sheet_name='Pins', index=False)
            return filepath
        else:
            # For CSV, save just the summary
            return self._save_data(user, 'full_report', 'csv')


def get_report_generator(output_dir: str = 'reports') -> ReportGenerator:
    """Get ReportGenerator instance"""
    return ReportGenerator(output_dir)
