"""
Pinterest Authentication Module (Community SDK)
Handles OAuth2 authentication using python-pinterest from sns-sdks
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)


class PinterestAuth:
    """Pinterest OAuth2 Authentication Handler"""
    
    def __init__(self):
        self.access_token = os.getenv('PINTEREST_ACCESS_TOKEN')
        
        # Optional - for OAuth flow
        self.app_id = os.getenv('PINTEREST_APP_ID')
        self.app_secret = os.getenv('PINTEREST_APP_SECRET')
        
    def is_configured(self) -> bool:
        """Check if access token is configured"""
        return bool(self.access_token and self.access_token != 'your_access_token_here')
    
    def get_api(self):
        """Get Pinterest API instance (sync)"""
        if not self.is_configured():
            self._show_setup_instructions()
            return None
            
        from pinterest import Api
        return Api(access_token=self.access_token)
    
    def get_async_api(self):
        """Get Pinterest AsyncAPI instance"""
        if not self.is_configured():
            self._show_setup_instructions()
            return None
            
        from pinterest import AsyncApi
        return AsyncApi(access_token=self.access_token)
    
    def _show_setup_instructions(self):
        """Show instructions for getting access token"""
        print("\n[!] Pinterest Access Token not configured!")
        print("\n" + "="*60)
        print("HOW TO GET ACCESS TOKEN:")
        print("="*60)
        print("""
1. Open https://developers.pinterest.com/tools/access_token/

2. Login to your Pinterest account

3. Select required scopes:
   - boards:read (read boards)
   - pins:read (read pins)
   - user_accounts:read (account info)

4. Click "Generate access token"

5. Copy the token and add to .env:
   PINTEREST_ACCESS_TOKEN=your_token_here
""")
        print(f"Path to .env: {env_path}")
        print("="*60)


def get_auth() -> PinterestAuth:
    """Get PinterestAuth instance"""
    return PinterestAuth()


def get_api():
    """Get configured Pinterest API instance"""
    return get_auth().get_api()


if __name__ == '__main__':
    # Test authentication
    auth = get_auth()
    if auth.is_configured():
        print(f"✓ Access Token configured: {auth.access_token[:20]}...")
    else:
        print("✗ Access Token not configured")
