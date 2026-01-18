"""
Pinterest Backup Tool
Backup all your pins and boards locally for protection
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import httpx

from .analytics import get_analytics
from .bulk_analyzer import get_bulk_analyzer


class BackupManager:
    """Backup Pinterest content locally"""
    
    def __init__(self, backup_dir: Optional[Path] = None):
        self.backup_dir = backup_dir or Path('backups')
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.analytics = get_analytics()
        self.bulk = get_bulk_analyzer()
        
    def create_backup(self, include_images: bool = False) -> Dict[str, Any]:
        """
        Create a full backup of account data
        
        Args:
            include_images: Whether to download pin images
            
        Returns:
            Backup summary
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = self.backup_dir / timestamp
        backup_path.mkdir(parents=True, exist_ok=True)
        
        print(f"Creating backup in: {backup_path}")
        
        result = {
            'timestamp': timestamp,
            'path': str(backup_path),
            'account': None,
            'boards': [],
            'pins': [],
            'images_downloaded': 0,
            'errors': [],
        }
        
        # Backup account info
        print("  Backing up account info...")
        try:
            account = self.analytics.get_user_account()
            result['account'] = account
            
            with open(backup_path / 'account.json', 'w', encoding='utf-8') as f:
                json.dump(account, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            result['errors'].append(f"Account: {e}")
        
        # Backup boards
        print("  Backing up boards...")
        try:
            boards = self.analytics.get_boards()
            result['boards'] = boards
            
            with open(backup_path / 'boards.json', 'w', encoding='utf-8') as f:
                json.dump(boards, f, indent=2, ensure_ascii=False, default=str)
            print(f"    Saved {len(boards)} boards")
        except Exception as e:
            result['errors'].append(f"Boards: {e}")
        
        # Backup pins
        print("  Backing up pins (this may take a while)...")
        try:
            pins = self.bulk.get_all_pins(use_cache=False)
            result['pins'] = pins
            
            with open(backup_path / 'pins.json', 'w', encoding='utf-8') as f:
                json.dump(pins, f, indent=2, ensure_ascii=False, default=str)
            print(f"    Saved {len(pins)} pins")
        except Exception as e:
            result['errors'].append(f"Pins: {e}")
        
        # Download images if requested
        if include_images and result['pins']:
            images_dir = backup_path / 'images'
            images_dir.mkdir(exist_ok=True)
            
            print(f"  Downloading images...")
            downloaded = self._download_images(result['pins'], images_dir)
            result['images_downloaded'] = downloaded
            print(f"    Downloaded {downloaded} images")
        
        # Save backup manifest
        manifest = {
            'created_at': datetime.now().isoformat(),
            'account_username': result['account'].get('username') if result['account'] else None,
            'total_boards': len(result['boards']),
            'total_pins': len(result['pins']),
            'images_downloaded': result['images_downloaded'],
            'errors': result['errors'],
        }
        
        with open(backup_path / 'manifest.json', 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        print(f"\nBackup complete: {backup_path}")
        return result
    
    def _download_images(self, pins: List[Dict], images_dir: Path, limit: int = 1000) -> int:
        """Download pin images"""
        downloaded = 0
        
        for i, pin in enumerate(pins[:limit]):
            if i > 0 and i % 50 == 0:
                print(f"    Progress: {i}/{min(len(pins), limit)}")
            
            # Get image URL
            image_url = None
            media = pin.get('media', {})
            
            if isinstance(media, dict):
                images = media.get('images', {})
                # Try to get original or largest size
                for size in ['original', '1200x', '600x', '400x300']:
                    if size in images:
                        image_url = images[size].get('url')
                        break
            
            if not image_url:
                # Try alternate field
                image_url = pin.get('image_url') or pin.get('image', {}).get('original', {}).get('url')
            
            if not image_url:
                continue
            
            # Download image
            try:
                pin_id = pin.get('id', f'unknown_{i}')
                ext = self._get_extension(image_url)
                filename = f"{pin_id}{ext}"
                filepath = images_dir / filename
                
                if not filepath.exists():
                    response = httpx.get(image_url, timeout=30, follow_redirects=True)
                    if response.status_code == 200:
                        with open(filepath, 'wb') as f:
                            f.write(response.content)
                        downloaded += 1
            except Exception:
                continue
        
        return downloaded
    
    def _get_extension(self, url: str) -> str:
        """Get file extension from URL"""
        if '.jpg' in url or '.jpeg' in url:
            return '.jpg'
        elif '.png' in url:
            return '.png'
        elif '.gif' in url:
            return '.gif'
        elif '.webp' in url:
            return '.webp'
        return '.jpg'
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups"""
        backups = []
        
        for item in self.backup_dir.iterdir():
            if item.is_dir():
                manifest_path = item / 'manifest.json'
                if manifest_path.exists():
                    with open(manifest_path, 'r', encoding='utf-8') as f:
                        manifest = json.load(f)
                    manifest['path'] = str(item)
                    manifest['folder'] = item.name
                    backups.append(manifest)
        
        # Sort by date (newest first)
        backups.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return backups
    
    def restore_info(self, backup_folder: str) -> Dict[str, Any]:
        """Get info about a backup for potential restore"""
        backup_path = self.backup_dir / backup_folder
        
        if not backup_path.exists():
            return {'error': f'Backup not found: {backup_folder}'}
        
        manifest_path = backup_path / 'manifest.json'
        if manifest_path.exists():
            with open(manifest_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {'error': 'Manifest not found'}


def get_backup_manager(backup_dir: Optional[Path] = None) -> BackupManager:
    """Get BackupManager instance"""
    return BackupManager(backup_dir)


if __name__ == '__main__':
    manager = get_backup_manager()
    result = manager.create_backup(include_images=False)
    print(json.dumps(result, indent=2, default=str))
