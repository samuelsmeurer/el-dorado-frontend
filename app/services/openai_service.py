import os
import tempfile
import requests
import subprocess
from openai import OpenAI
from typing import Optional
from ..core.config import settings
import io


class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.max_file_size = 25 * 1024 * 1024  # 25MB limit for OpenAI
    
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
    
    def check_file_size_limit(self, video_path: str) -> bool:
        """Check if file size is within OpenAI limits"""
        try:
            file_size = os.path.getsize(video_path)
            size_mb = file_size / (1024 * 1024)
            print(f"[DEBUG] File size: {file_size} bytes ({size_mb:.1f}MB)")
            
            if file_size > self.max_file_size:
                print(f"[DEBUG] File too large: {size_mb:.1f}MB > {self.max_file_size / (1024*1024):.1f}MB")
                return False
            
            print("[DEBUG] File size OK")
            return True
            
        except Exception as e:
            print(f"[DEBUG] Error checking file size: {str(e)}")
            return True  # Continue if we can't check
    
    def transcribe_video(self, video_path: str) -> str:
        """Transcribe video using OpenAI Whisper API"""
        try:
            print(f"[DEBUG] Opening file for transcription: {video_path}")
            with open(video_path, "rb") as audio_file:
                print(f"[DEBUG] Sending to OpenAI Whisper...")
                transcription = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="pt"  # Portuguese
                )
                print(f"[DEBUG] OpenAI response received")
            return transcription.text
            
        except Exception as e:
            print(f"[DEBUG] Transcription error: {str(e)}")
            raise Exception(f"Erro na transcrição: {str(e)}")
        finally:
            # Clean up temporary file
            print(f"[DEBUG] Cleaning up temp file: {video_path}")
            if os.path.exists(video_path):
                try:
                    os.unlink(video_path)
                    print(f"[DEBUG] Temp file deleted successfully")
                except Exception as cleanup_error:
                    print(f"[DEBUG] Failed to delete temp file: {cleanup_error}")
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
        """Download video to disk and transcribe (more reliable than streaming)"""
        video_path = None
        try:
            print(f"[DEBUG] Starting download from: {video_url}")
            # Download video to temporary file
            video_path = self.download_video(video_url)
            print(f"[DEBUG] Downloaded to: {video_path}, size: {os.path.getsize(video_path)} bytes")
            
            # Check file size limit
            if not self.check_file_size_limit(video_path):
                size_mb = os.path.getsize(video_path) / (1024 * 1024)
                raise Exception(f"Arquivo muito grande ({size_mb:.1f}MB). O limite máximo é 25MB. Tente um vídeo menor ou de menor qualidade.")
            
            # Transcribe from downloaded file
            print(f"[DEBUG] Starting transcription...")
            result = self.transcribe_video(video_path)
            print(f"[DEBUG] Transcription successful, length: {len(result)} chars")
            return result
            
        except Exception as e:
            print(f"[DEBUG] Error occurred: {str(e)}")
            # Clean up in case of error
            if video_path and os.path.exists(video_path):
                try:
                    os.unlink(video_path)
                    print(f"[DEBUG] Cleaned up temp file: {video_path}")
                except:
                    pass
            raise Exception(f"Erro no download e transcrição: {str(e)}")