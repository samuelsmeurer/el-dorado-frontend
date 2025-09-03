import requests
from datetime import datetime
from typing import Optional, List, Dict, Any
from ..core.config import settings


class ScrapTikService:
    """
    ScrapTik API integration service adapted for El Dorado system
    Based on the existing count_videos_api implementation
    """
    
    def __init__(self, rapidapi_key: Optional[str] = None):
        self.rapidapi_key = rapidapi_key or settings.rapidapi_key
        self.headers = {
            "X-RapidAPI-Host": settings.rapidapi_host,
            "X-RapidAPI-Key": self.rapidapi_key
        }
    
    def get_user_id_from_username(self, username: str) -> Optional[str]:
        """
        Convert TikTok username to user ID using ScrapTik API
        
        Args:
            username: TikTok username (without @)
            
        Returns:
            User ID string if found, None otherwise
        """
        url = f"https://{settings.rapidapi_host}/username-to-id"
        params = {"username": username.replace("@", "")}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            # Try different possible response formats
            if 'uid' in result:
                return result['uid']
            elif 'user_id' in result:
                return result['user_id']
            elif 'data' in result and 'user_id' in result['data']:
                return result['data']['user_id']
            elif 'id' in result:
                return result['id']
            else:
                print(f"Unexpected response format: {result}")
                return None
                
        except requests.RequestException as e:
            print(f"Error getting user ID for {username}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error for {username}: {e}")
            return None
    
    def get_user_posts(self, user_id: str, count: int = None) -> Optional[Dict[str, Any]]:
        """
        Get user's recent posts using ScrapTik API
        
        Args:
            user_id: TikTok user ID
            count: Number of videos to fetch (default from settings)
            
        Returns:
            API response with videos data or None if error
        """
        url = f"https://{settings.rapidapi_host}/user-posts"
        params = {
            "user_id": user_id,
            "count": count or settings.sync_video_count,
            "region": "GB"
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=60)
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            print(f"Error getting posts for user {user_id}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error for user {user_id}: {e}")
            return None
    
    def filter_eldorado_videos(self, videos_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filter videos that contain @El Dorado P2P mention
        Based on the actual API response structure from your sample data
        
        Args:
            videos_data: Raw response from user-posts API
            
        Returns:
            List of sponsored videos with extracted data
        """
        sponsored_videos = []
        target_mention = settings.eldorado_mention.lower()
        
        # Handle different response formats (aweme_list or data)
        videos = videos_data.get('aweme_list', videos_data.get('data', []))
        
        for video in videos:
            try:
                # Get description
                description = video.get('desc', '')
                
                # Check for El Dorado mention (case-insensitive)
                if target_mention not in description.lower():
                    continue
                
                # Extract video data based on actual API structure
                video_id = video.get('aweme_id') or video.get('id')
                create_time = video.get('create_time')
                statistics = video.get('statistics', {})
                
                # Extract URLs (try different possible paths)
                video_urls = video.get('video', {})
                download_url = None
                if 'play_addr' in video_urls:
                    url_list = video_urls['play_addr'].get('url_list', [])
                    download_url = url_list[0] if url_list else None
                elif 'download_addr' in video_urls:
                    download_url = video_urls.get('download_addr')
                
                # Web URL for public access
                web_url = video.get('share_url') or f"https://www.tiktok.com/@{video.get('author', {}).get('unique_id', '')}/video/{video_id}"
                
                sponsored_video = {
                    'tiktok_video_id': str(video_id),
                    'description': description,
                    'published_at': datetime.fromtimestamp(int(create_time)) if create_time else None,
                    'view_count': statistics.get('play_count', 0),
                    'like_count': statistics.get('digg_count', 0),
                    'comment_count': statistics.get('comment_count', 0),
                    'share_count': statistics.get('share_count', 0),
                    'public_video_url': web_url,
                    'watermark_free_url': download_url
                }
                
                sponsored_videos.append(sponsored_video)
                
            except Exception as e:
                print(f"Error processing video {video.get('aweme_id', 'unknown')}: {e}")
                continue
        
        return sponsored_videos
    
    def get_video_info_by_url(self, video_url: str) -> Optional[Dict[str, Any]]:
        """
        Get video information from a TikTok URL (including short URLs)
        
        Args:
            video_url: TikTok video URL (full or short)
            
        Returns:
            Video information dict with tiktok_video_id, or None if error
        """
        url = f"https://{settings.rapidapi_host}/video-info"
        params = {"video_url": video_url}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            # Extract video ID from different response formats
            video_id = None
            if 'aweme_id' in result:
                video_id = result['aweme_id']
            elif 'data' in result and 'aweme_id' in result['data']:
                video_id = result['data']['aweme_id']
            elif 'id' in result:
                video_id = result['id']
            elif 'video_id' in result:
                video_id = result['video_id']
            
            if video_id:
                return {'tiktok_video_id': str(video_id)}
            else:
                return None
                
        except requests.RequestException as e:
            print(f"Error getting video info for {video_url}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error getting video info: {e}")
            return None

    def get_eldorado_videos(self, username: str) -> List[Dict[str, Any]]:
        """
        Complete pipeline: username → user_id → posts → filter El Dorado videos
        
        Args:
            username: TikTok username
            
        Returns:
            List of sponsored videos ready for database insertion
        """
        # Step 1: Get user ID
        user_id = self.get_user_id_from_username(username)
        if not user_id:
            return []
        
        # Step 2: Get recent posts
        posts_data = self.get_user_posts(user_id)
        if not posts_data:
            return []
        
        # Step 3: Filter El Dorado videos
        sponsored_videos = self.filter_eldorado_videos(posts_data)
        
        return sponsored_videos