import os
import tempfile
import requests
from openai import OpenAI
from typing import Optional
from ..core.config import settings
import io


class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
    
    def download_video(self, video_url: str) -> str:
        """Download video to temporary file and return file path"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'video/mp4,video/*,*/*;q=0.9',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            response = requests.get(video_url, stream=True, timeout=120, headers=headers)
            response.raise_for_status()
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    tmp_file.write(chunk)
                return tmp_file.name
                
        except Exception as e:
            raise Exception(f"Erro ao baixar vídeo: {str(e)}")
    
    def transcribe_video(self, video_path: str) -> str:
        """Transcribe video using OpenAI Whisper API"""
        try:
            with open(video_path, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="pt"  # Portuguese
                )
            return transcription.text
            
        except Exception as e:
            raise Exception(f"Erro na transcrição: {str(e)}")
        finally:
            # Clean up temporary file
            if os.path.exists(video_path):
                try:
                    os.unlink(video_path)
                except:
                    pass
    
    def transcribe_from_url_streaming(self, video_url: str) -> str:
        """Stream video directly to OpenAI without saving to disk"""
        try:
            # Download video to memory with proper headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'video/mp4,video/*,*/*;q=0.9',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            response = requests.get(video_url, timeout=120, headers=headers)
            response.raise_for_status()
            
            # Create a file-like object from bytes
            video_bytes = io.BytesIO(response.content)
            video_bytes.name = "video.mp4"  # OpenAI needs a filename
            
            # Send directly to OpenAI
            transcription = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=video_bytes,
                language="pt"
            )
            
            return transcription.text
            
        except Exception as e:
            raise Exception(f"Erro na transcrição streaming: {str(e)}")
    
    def transcribe_from_url(self, video_url: str) -> str:
        """Try streaming first, fallback to download if needed"""
        try:
            # Try streaming approach first (no disk usage)
            return self.transcribe_from_url_streaming(video_url)
            
        except Exception as streaming_error:
            print(f"Streaming failed: {streaming_error}, trying download method...")
            
            # Fallback to download method
            video_path = None
            try:
                # Download video
                video_path = self.download_video(video_url)
                
                # Transcribe
                return self.transcribe_video(video_path)
                
            except Exception as download_error:
                # Clean up in case of error
                if video_path and os.path.exists(video_path):
                    try:
                        os.unlink(video_path)
                    except:
                        pass
                raise Exception(f"Ambos métodos falharam - Streaming: {streaming_error}, Download: {download_error}")