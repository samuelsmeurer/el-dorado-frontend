import requests
from typing import Optional
from urllib.parse import urlparse

class URLExpander:
    """Service to expand short URLs, specifically for TikTok vm.tiktok.com links"""
    
    @staticmethod
    def expand_tiktok_url(url: str) -> str:
        """
        Expand TikTok short URLs (vm.tiktok.com) to full URLs
        
        Args:
            url: TikTok URL (short or full)
            
        Returns:
            str: Expanded URL or original URL if expansion fails
        """
        url = url.strip()
        
        # If it's already a full TikTok URL, return as is
        if "tiktok.com/@" in url and "/video/" in url:
            return url
            
        # If it's a vm.tiktok.com short URL, expand it
        if "vm.tiktok.com/" in url:
            try:
                # Follow redirects to get the full URL
                headers = {
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1'
                }
                
                # Use HEAD request to get redirect without downloading content
                response = requests.head(url, allow_redirects=True, timeout=10, headers=headers)
                
                # The final URL after all redirects
                expanded_url = response.url
                
                # Clean up any tracking parameters but keep essential ones
                if "tiktok.com/@" in expanded_url and "/video/" in expanded_url:
                    # Extract the clean URL parts
                    parsed = urlparse(expanded_url)
                    clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                    return clean_url
                    
                return expanded_url
                
            except Exception as e:
                print(f"[DEBUG] Failed to expand URL {url}: {str(e)}")
                # Return original URL if expansion fails
                return url
        
        # Return original URL if it's not a short URL
        return url
    
    @staticmethod
    def extract_video_id_from_url(url: str) -> Optional[str]:
        """
        Extract TikTok video ID from URL (short or full)
        
        Args:
            url: TikTok URL
            
        Returns:
            Optional[str]: Video ID if found, None otherwise
        """
        try:
            # First expand the URL if it's a short URL
            expanded_url = URLExpander.expand_tiktok_url(url)
            
            # Extract video ID from expanded URL
            if "/video/" in expanded_url:
                video_id = expanded_url.split("/video/")[-1].split("?")[0].split("/")[0]
                return video_id
                
            return None
            
        except Exception as e:
            print(f"[DEBUG] Failed to extract video ID from {url}: {str(e)}")
            return None