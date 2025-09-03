import os
import tempfile
import requests
import subprocess
from openai import OpenAI
from typing import Optional
from ..core.config import settings
import io
try:
    from moviepy.editor import VideoFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    print("[WARNING] MoviePy não disponível - compressão de vídeo desabilitada")


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
    
    def extract_audio_from_video(self, video_path: str) -> str:
        """Extract audio from video to reduce file size"""
        if not MOVIEPY_AVAILABLE:
            raise Exception("MoviePy não disponível para extração de áudio")
        
        audio_path = None
        try:
            print(f"[DEBUG] Extraindo áudio do vídeo: {video_path}")
            
            # Load video and extract audio
            with VideoFileClip(video_path) as video:
                audio = video.audio
                
                # Create temporary audio file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_audio:
                    audio_path = tmp_audio.name
                
                # Write audio to file
                audio.write_audiofile(audio_path, verbose=False, logger=None)
                
            print(f"[DEBUG] Áudio extraído: {audio_path}")
            return audio_path
            
        except Exception as e:
            if audio_path and os.path.exists(audio_path):
                os.unlink(audio_path)
            raise Exception(f"Erro ao extrair áudio: {str(e)}")
    
    def compress_video(self, video_path: str, target_size_mb: float = 20) -> str:
        """Compress video to target size"""
        if not MOVIEPY_AVAILABLE:
            raise Exception("MoviePy não disponível para compressão")
        
        compressed_path = None
        try:
            print(f"[DEBUG] Comprimindo vídeo para ~{target_size_mb}MB")
            
            # Create temporary compressed file
            with tempfile.NamedTemporaryFile(delete=False, suffix='_compressed.mp4') as tmp_compressed:
                compressed_path = tmp_compressed.name
            
            with VideoFileClip(video_path) as video:
                # Calculate target bitrate based on duration and target size
                duration = video.duration
                target_bitrate = int((target_size_mb * 8 * 1024) / duration)  # kbps
                
                # Limit bitrate to reasonable range
                target_bitrate = max(200, min(target_bitrate, 2000))  # 200-2000 kbps
                
                print(f"[DEBUG] Duração: {duration}s, Bitrate alvo: {target_bitrate}kbps")
                
                # Compress video
                video.write_videofile(
                    compressed_path,
                    bitrate=f"{target_bitrate}k",
                    verbose=False,
                    logger=None
                )
            
            compressed_size = os.path.getsize(compressed_path) / (1024 * 1024)
            print(f"[DEBUG] Vídeo comprimido: {compressed_size:.1f}MB")
            
            return compressed_path
            
        except Exception as e:
            if compressed_path and os.path.exists(compressed_path):
                os.unlink(compressed_path)
            raise Exception(f"Erro na compressão: {str(e)}")
    
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
        """Download video to disk and transcribe with compression if needed"""
        video_path = None
        processed_path = None
        try:
            print(f"[DEBUG] Starting download from: {video_url}")
            # Download video to temporary file
            video_path = self.download_video(video_url)
            original_size = os.path.getsize(video_path) / (1024 * 1024)
            print(f"[DEBUG] Downloaded to: {video_path}, size: {original_size:.1f}MB")
            
            # Check if file needs processing
            if self.check_file_size_limit(video_path):
                # File is small enough, use directly
                processed_path = video_path
            else:
                print(f"[DEBUG] Arquivo muito grande ({original_size:.1f}MB), tentando compressão...")
                
                if not MOVIEPY_AVAILABLE:
                    raise Exception(f"Arquivo muito grande ({original_size:.1f}MB). O limite máximo é 25MB. MoviePy não disponível para compressão.")
                
                try:
                    # Try audio extraction first (smaller file)
                    print(f"[DEBUG] Tentando extrair apenas áudio...")
                    processed_path = self.extract_audio_from_video(video_path)
                    
                    audio_size = os.path.getsize(processed_path) / (1024 * 1024)
                    print(f"[DEBUG] Áudio extraído: {audio_size:.1f}MB")
                    
                    if not self.check_file_size_limit(processed_path):
                        # Audio still too big, try video compression
                        print(f"[DEBUG] Áudio ainda grande, tentando compressão de vídeo...")
                        if processed_path != video_path:
                            os.unlink(processed_path)
                        
                        processed_path = self.compress_video(video_path, target_size_mb=20)
                        compressed_size = os.path.getsize(processed_path) / (1024 * 1024)
                        
                        if not self.check_file_size_limit(processed_path):
                            raise Exception(f"Mesmo após compressão ({compressed_size:.1f}MB), arquivo ainda muito grande. Limite: 25MB.")
                    
                except Exception as compression_error:
                    print(f"[DEBUG] Erro na compressão: {compression_error}")
                    raise Exception(f"Arquivo muito grande ({original_size:.1f}MB) e falha na compressão: {str(compression_error)}")
            
            # Transcribe from processed file
            print(f"[DEBUG] Starting transcription...")
            final_size = os.path.getsize(processed_path) / (1024 * 1024)
            print(f"[DEBUG] Processando arquivo de {final_size:.1f}MB")
            
            result = self.transcribe_video(processed_path)
            print(f"[DEBUG] Transcription successful, length: {len(result)} chars")
            return result
            
        except Exception as e:
            print(f"[DEBUG] Error occurred: {str(e)}")
            # Clean up in case of error
            for path in [video_path, processed_path]:
                if path and os.path.exists(path):
                    try:
                        os.unlink(path)
                        print(f"[DEBUG] Cleaned up temp file: {path}")
                    except:
                        pass
            raise Exception(f"Erro no download e transcrição: {str(e)}")