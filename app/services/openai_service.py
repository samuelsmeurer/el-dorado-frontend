import os
import tempfile
import requests
import subprocess
import re
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
    
    def get_fresh_video_url(self, tiktok_url: str) -> str:
        """Get a fresh video URL from TikTok page"""
        try:
            print(f"[DEBUG] Buscando URL fresco para: {tiktok_url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = requests.get(tiktok_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Look for video URLs in the page source
            content = response.text
            
            # Pattern to match TikTok CDN video URLs
            video_patterns = [
                r'"downloadAddr":"([^"]*tiktokcdn[^"]*\.mp4[^"]*)"',
                r'"playAddr":"([^"]*tiktokcdn[^"]*\.mp4[^"]*)"',
                r'src="([^"]*tiktokcdn[^"]*\.mp4[^"]*)"',
                r'video[^>]*src="([^"]*)"'
            ]
            
            for pattern in video_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    # Clean up URL (remove escaping)
                    clean_url = match.replace('\\u002F', '/').replace('\\/', '/')
                    if 'tiktokcdn' in clean_url and '.mp4' in clean_url:
                        print(f"[DEBUG] URL fresco encontrado: {clean_url[:100]}...")
                        return clean_url
            
            print("[DEBUG] Nenhum URL de vídeo encontrado na página")
            return None
            
        except Exception as e:
            print(f"[DEBUG] Erro ao buscar URL fresco: {str(e)}")
            return None
    
    def download_video(self, video_url: str) -> str:
        """Download video to temporary file and return file path"""
        try:
            # Enhanced headers to bypass TikTok restrictions
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'identity',  # Don't use compression to avoid issues
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'video',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'cross-site',
                'Range': 'bytes=0-'  # Request full range
            }
            
            # Try multiple attempts with different strategies
            for attempt in range(3):
                try:
                    print(f"[DEBUG] Tentativa {attempt + 1} de download: {video_url}")
                    
                    # Use session to maintain cookies
                    session = requests.Session()
                    session.headers.update(headers)
                    
                    response = session.get(video_url, stream=True, timeout=120, allow_redirects=True)
                    
                    if response.status_code == 403:
                        print(f"[DEBUG] 403 na tentativa {attempt + 1}, tentando com headers diferentes...")
                        if attempt < 2:  # Try different user agent on retry
                            headers['User-Agent'] = f'TikTok 26.1.0 rv:261013 (iPhone; iOS 16.6; en_US) Cronet'
                            continue
                    
                    response.raise_for_status()
                    
                    # Check if we got actual video content
                    content_type = response.headers.get('content-type', '')
                    if 'video' not in content_type and 'octet-stream' not in content_type:
                        print(f"[DEBUG] Content-Type inesperado: {content_type}")
                    
                    # Create temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                        total_size = 0
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:  # Filter out keep-alive chunks
                                tmp_file.write(chunk)
                                total_size += len(chunk)
                        
                        print(f"[DEBUG] Download concluído: {total_size} bytes")
                        return tmp_file.name
                        
                except requests.exceptions.RequestException as req_error:
                    print(f"[DEBUG] Erro na tentativa {attempt + 1}: {req_error}")
                    if attempt == 2:  # Last attempt
                        raise req_error
                    continue
                    
        except Exception as e:
            error_msg = str(e)
            if "403" in error_msg:
                raise Exception(f"Erro 403: Acesso negado pelo TikTok. O link pode ter expirado ou estar protegido. Tente com um vídeo mais recente.")
            elif "404" in error_msg:
                raise Exception(f"Erro 404: Vídeo não encontrado. Verifique se o link está correto.")
            else:
                raise Exception(f"Erro ao baixar vídeo: {error_msg}")
    
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
            # Download video to memory with enhanced headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'identity',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'video',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'cross-site'
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