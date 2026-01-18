"""
Pinterest Analytics Security Module
Protects API tokens and sensitive data from leaks
"""

import os
import sys
import stat
from pathlib import Path
from typing import Optional
import hashlib


class SecurityManager:
    """Manage API token security"""
    
    ENV_FILE = '.env'
    SENSITIVE_FILES = ['.env', '.env.local', '.env.production', 'credentials.json']
    
    def __init__(self):
        self.project_root = Path('.')
    
    def check_env_security(self) -> dict:
        """
        Check if .env file is properly secured
        
        Returns:
            Security check results
        """
        results = {
            'secure': True,
            'issues': [],
            'recommendations': [],
        }
        
        env_path = self.project_root / self.ENV_FILE
        
        # Check if .env exists
        if not env_path.exists():
            results['issues'].append('.env file not found')
            results['recommendations'].append('Run: python setup.py')
            return results
        
        # Check if .env is in .gitignore
        gitignore_path = self.project_root / '.gitignore'
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                gitignore_content = f.read()
                if '.env' not in gitignore_content:
                    results['secure'] = False
                    results['issues'].append('.env is NOT in .gitignore!')
                    results['recommendations'].append('Add .env to .gitignore immediately')
        else:
            results['secure'] = False
            results['issues'].append('No .gitignore file found')
            results['recommendations'].append('Create .gitignore with .env entry')
        
        # Check file permissions (Unix only)
        if os.name != 'nt':  # Not Windows
            try:
                mode = os.stat(env_path).st_mode
                if mode & stat.S_IROTH:  # Others can read
                    results['secure'] = False
                    results['issues'].append('.env is world-readable')
                    results['recommendations'].append('Run: chmod 600 .env')
            except:
                pass
        
        # Check if token is exposed in any tracked files
        git_dir = self.project_root / '.git'
        if git_dir.exists():
            token = self._get_token_from_env()
            if token:
                exposed = self._check_token_in_repo(token)
                if exposed:
                    results['secure'] = False
                    results['issues'].append('Token may be exposed in git history!')
                    results['recommendations'].append('Revoke and regenerate your token')
        
        if not results['issues']:
            results['issues'].append('All checks passed')
        
        return results
    
    def _get_token_from_env(self) -> Optional[str]:
        """Get token from .env file"""
        env_path = self.project_root / self.ENV_FILE
        if not env_path.exists():
            return None
        
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('PINTEREST_ACCESS_TOKEN='):
                    return line.split('=', 1)[1].strip().strip('"').strip("'")
        return None
    
    def _check_token_in_repo(self, token: str) -> bool:
        """Check if token appears in git-tracked files"""
        # Only check first 10 chars to avoid false negatives from partial matches
        token_prefix = token[:10] if len(token) > 10 else token
        
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'grep', '-l', token_prefix],
                capture_output=True,
                text=True,
                cwd=str(self.project_root)
            )
            return bool(result.stdout.strip())
        except:
            return False
    
    def mask_token(self, token: str) -> str:
        """Mask token for safe display"""
        if not token or len(token) < 8:
            return '****'
        return token[:4] + '*' * (len(token) - 8) + token[-4:]
    
    def get_token_hash(self, token: str) -> str:
        """Get SHA256 hash of token for logging without exposing it"""
        return hashlib.sha256(token.encode()).hexdigest()[:16]
    
    def validate_token_format(self, token: str) -> dict:
        """
        Validate token format
        
        Returns:
            Validation result
        """
        result = {
            'valid': True,
            'issues': [],
        }
        
        if not token:
            result['valid'] = False
            result['issues'].append('Token is empty')
            return result
        
        if len(token) < 20:
            result['valid'] = False
            result['issues'].append('Token appears too short')
        
        if ' ' in token or '\n' in token:
            result['valid'] = False
            result['issues'].append('Token contains whitespace')
        
        # Check for common mistakes
        if token.startswith('<') or token.endswith('>'):
            result['valid'] = False
            result['issues'].append('Token appears to be a placeholder')
        
        if token.lower() in ['your_token_here', 'paste_token_here', 'xxx']:
            result['valid'] = False
            result['issues'].append('Token is a placeholder value')
        
        return result
    
    def secure_print(self, message: str, token: str = None):
        """Print message with masked token"""
        if token and token in message:
            message = message.replace(token, self.mask_token(token))
        print(message)
    
    def get_security_tips(self) -> list:
        """Get security best practices"""
        return [
            "Never commit .env to git",
            "Use environment variables in production",
            "Rotate tokens regularly",
            "Use minimum required API scopes",
            "Set token expiry when possible",
            "Monitor API usage for unusual activity",
            "Keep python-pinterest SDK updated",
            "Don't share tokens in support requests",
        ]


def get_security_manager() -> SecurityManager:
    """Get SecurityManager instance"""
    return SecurityManager()


def check_security():
    """Run security check and print results"""
    manager = get_security_manager()
    results = manager.check_env_security()
    
    print("\n=== Security Check ===\n")
    
    if results['secure']:
        print("✅ Security Status: GOOD\n")
    else:
        print("⚠️  Security Status: ISSUES FOUND\n")
    
    print("Checks:")
    for issue in results['issues']:
        icon = "✓" if "passed" in issue.lower() else "✗"
        print(f"  {icon} {issue}")
    
    if results['recommendations']:
        print("\nRecommendations:")
        for rec in results['recommendations']:
            print(f"  → {rec}")
    
    print("\nSecurity Tips:")
    for tip in manager.get_security_tips()[:5]:
        print(f"  • {tip}")


if __name__ == '__main__':
    check_security()
