from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from ..core.database import get_db
from ..models import Influencer, InfluencerIds, TikTokVideo
from ..schemas import TikTokVideoResponse, VideoSyncResponse, VideoTranscriptionRequest, VideoTranscriptionResponse
from ..services import ScrapTikService, OpenAIService, URLExpander

router = APIRouter(prefix="/api/v1/videos", tags=["videos"])


@router.get("/", response_model=List[TikTokVideoResponse])
def list_sponsored_videos(
    skip: int = 0,
    limit: int = 100,
    eldorado_username: str = None,
    db: Session = Depends(get_db)
):
    """List sponsored videos with optional filtering by influencer"""
    query = db.query(TikTokVideo)
    
    if eldorado_username:
        query = query.filter(TikTokVideo.eldorado_username == eldorado_username)
    
    videos = query.order_by(desc(TikTokVideo.published_at)).offset(skip).limit(limit).all()
    return videos


@router.get("/{video_id}", response_model=TikTokVideoResponse)
def get_video(
    video_id: str,
    db: Session = Depends(get_db)
):
    """Get specific video by ID"""
    video = db.query(TikTokVideo).filter(
        TikTokVideo.tiktok_video_id == video_id
    ).first()
    
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video '{video_id}' not found"
        )
    
    return video


@router.post("/sync/all", response_model=List[VideoSyncResponse])
def sync_all_influencers_videos(
    db: Session = Depends(get_db)
):
    """Sync sponsored videos for all active influencers"""
    
    # Get all active influencers
    active_influencers = db.query(Influencer).filter(
        Influencer.status == "active"
    ).all()
    
    results = []
    
    for influencer in active_influencers:
        try:
            # Use the single influencer sync endpoint logic
            influencer_ids = db.query(InfluencerIds).filter(
                InfluencerIds.eldorado_username == influencer.eldorado_username
            ).first()
            
            if not influencer_ids or not influencer_ids.tiktok_username or not influencer_ids.tiktok_id:
                results.append(VideoSyncResponse(
                    success=False,
                    message=f"Skipping {influencer.eldorado_username} - Missing TikTok data",
                    videos_processed=0,
                    new_videos=0,
                    updated_videos=0,
                    errors=[f"Missing TikTok username or ID - use /sync-tiktok-id first"]
                ))
                continue
            
            # Sync videos for this influencer
            scraptik = ScrapTikService()
            sponsored_videos = scraptik.get_eldorado_videos(influencer_ids.tiktok_username)
            
            new_videos = 0
            updated_videos = 0
            errors = []
            
            for video_data in sponsored_videos:
                try:
                    existing_video = db.query(TikTokVideo).filter(
                        TikTokVideo.tiktok_video_id == video_data['tiktok_video_id']
                    ).first()
                    
                    if existing_video:
                        # Update metrics
                        existing_video.view_count = video_data['view_count']
                        existing_video.like_count = video_data['like_count']
                        existing_video.comment_count = video_data['comment_count']
                        existing_video.share_count = video_data['share_count']
                        
                        # Always update URLs (they might have changed)
                        existing_video.public_video_url = video_data['public_video_url']
                        existing_video.watermark_free_url = video_data['watermark_free_url']
                        existing_video.watermark_free_url_alt1 = video_data.get('watermark_free_url_alt1')
                        existing_video.watermark_free_url_alt2 = video_data.get('watermark_free_url_alt2')
                        
                        updated_videos += 1
                    else:
                        new_video = TikTokVideo(
                            eldorado_username=influencer.eldorado_username,
                            tiktok_username=influencer_ids.tiktok_username,
                            tiktok_video_id=video_data['tiktok_video_id'],
                            description=video_data['description'],
                            view_count=video_data['view_count'],
                            like_count=video_data['like_count'],
                            comment_count=video_data['comment_count'],
                            share_count=video_data['share_count'],
                            public_video_url=video_data['public_video_url'],
                            watermark_free_url=video_data['watermark_free_url'],
                            watermark_free_url_alt1=video_data.get('watermark_free_url_alt1'),
                            watermark_free_url_alt2=video_data.get('watermark_free_url_alt2'),
                            published_at=video_data['published_at']
                        )
                        db.add(new_video)
                        new_videos += 1
                        
                except Exception as e:
                    errors.append(f"Video {video_data.get('tiktok_video_id', 'unknown')}: {str(e)}")
            
            db.commit()
            
            results.append(VideoSyncResponse(
                success=True,
                message=f"Sync completed for {influencer.eldorado_username}",
                videos_processed=len(sponsored_videos),
                new_videos=new_videos,
                updated_videos=updated_videos,
                errors=errors
            ))
            
        except Exception as e:
            db.rollback()
            results.append(VideoSyncResponse(
                success=False,
                message=f"Error syncing {influencer.eldorado_username}: {str(e)}",
                videos_processed=0,
                new_videos=0,
                updated_videos=0,
                errors=[str(e)]
            ))
    
    return results


@router.post("/sync/{eldorado_username}", response_model=VideoSyncResponse)
def sync_influencer_videos(
    eldorado_username: str,
    db: Session = Depends(get_db)
):
    """Sync sponsored videos for a specific influencer"""
    
    # Get influencer
    influencer = db.query(Influencer).filter(
        Influencer.eldorado_username == eldorado_username
    ).first()
    
    if not influencer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Influencer '{eldorado_username}' not found"
        )
    
    # Get influencer social IDs
    influencer_ids = db.query(InfluencerIds).filter(
        InfluencerIds.eldorado_username == eldorado_username
    ).first()
    
    if not influencer_ids or not influencer_ids.tiktok_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No TikTok username found for '{eldorado_username}'"
        )
    
    # Skip if no TikTok ID (avoid unnecessary API calls)
    if not influencer_ids.tiktok_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No TikTok ID found for '{eldorado_username}'. Please sync TikTok ID first using /sync-tiktok-id endpoint."
        )
    
    # Get sponsored videos using ScrapTik
    scraptik = ScrapTikService()
    sponsored_videos = scraptik.get_eldorado_videos(influencer_ids.tiktok_username)
    
    new_videos = 0
    updated_videos = 0
    errors = []
    
    for video_data in sponsored_videos:
        try:
            # Check if video already exists
            existing_video = db.query(TikTokVideo).filter(
                TikTokVideo.tiktok_video_id == video_data['tiktok_video_id']
            ).first()
            
            if existing_video:
                # UPDATE existing video metrics
                existing_video.view_count = video_data['view_count']
                existing_video.like_count = video_data['like_count']
                existing_video.comment_count = video_data['comment_count']
                existing_video.share_count = video_data['share_count']
                
                # Always update URLs (they might have changed)
                existing_video.public_video_url = video_data['public_video_url']
                existing_video.watermark_free_url = video_data['watermark_free_url']
                existing_video.watermark_free_url_alt1 = video_data.get('watermark_free_url_alt1')
                existing_video.watermark_free_url_alt2 = video_data.get('watermark_free_url_alt2')
                
                updated_videos += 1
            else:
                # INSERT new sponsored video
                new_video = TikTokVideo(
                    eldorado_username=eldorado_username,
                    tiktok_username=influencer_ids.tiktok_username,
                    tiktok_video_id=video_data['tiktok_video_id'],
                    description=video_data['description'],
                    view_count=video_data['view_count'],
                    like_count=video_data['like_count'],
                    comment_count=video_data['comment_count'],
                    share_count=video_data['share_count'],
                    public_video_url=video_data['public_video_url'],
                    watermark_free_url=video_data['watermark_free_url'],
                    watermark_free_url_alt1=video_data.get('watermark_free_url_alt1'),
                    watermark_free_url_alt2=video_data.get('watermark_free_url_alt2'),
                    published_at=video_data['published_at']
                )
                db.add(new_video)
                new_videos += 1
                
        except Exception as e:
            errors.append(f"Error processing video {video_data.get('tiktok_video_id', 'unknown')}: {str(e)}")
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    
    return VideoSyncResponse(
        success=True,
        message=f"Sync completed for {eldorado_username}",
        videos_processed=len(sponsored_videos),
        new_videos=new_videos,
        updated_videos=updated_videos,
        errors=errors
    )


@router.post("/transcribe", response_model=VideoTranscriptionResponse)
def transcribe_video_from_url(
    request: VideoTranscriptionRequest,
    db: Session = Depends(get_db)
):
    """Transcribe TikTok video from URL using OpenAI Whisper"""
    
    try:
        # Extract video ID from TikTok URL
        tiktok_url = request.tiktok_url.strip()
        
        # Basic URL validation
        if not tiktok_url or not ("tiktok.com" in tiktok_url or "vm.tiktok.com" in tiktok_url):
            return VideoTranscriptionResponse(
                success=False,
                message="URL inválida. Forneça uma URL válida do TikTok."
            )
        
        # Expand URL if it's a short URL and extract video ID
        print(f"[DEBUG] Original URL: {tiktok_url}")
        
        # Expand short URLs to full URLs
        expanded_url = URLExpander.expand_tiktok_url(tiktok_url)
        print(f"[DEBUG] Expanded URL: {expanded_url}")
        
        # Extract video ID from expanded URL
        video_id = URLExpander.extract_video_id_from_url(expanded_url)
        print(f"[DEBUG] Extracted video ID: {video_id}")
        
        if not video_id:
            return VideoTranscriptionResponse(
                success=False,
                message="Não foi possível extrair o ID do vídeo da URL fornecida. Tente usar uma URL válida do TikTok."
            )
        
        # Search for video in database using public_video_url
        video = db.query(TikTokVideo).filter(
            TikTokVideo.public_video_url.contains(video_id)
        ).first()
        
        if not video:
            # Try searching by tiktok_video_id as fallback
            video = db.query(TikTokVideo).filter(
                TikTokVideo.tiktok_video_id == video_id
            ).first()
        
        # If still not found and we have a short URL, try broader search
        if not video and "vm.tiktok.com/" in tiktok_url:
            short_id = tiktok_url.split("vm.tiktok.com/")[-1].rstrip("/").split("?")[0]
            # Try to find video by searching for the short ID in any URL field
            video = db.query(TikTokVideo).filter(
                TikTokVideo.public_video_url.contains(short_id)
            ).first()
        
        if not video:
            return VideoTranscriptionResponse(
                success=True,
                message="Este vídeo não é de um influenciador cadastrado.",
                video_found=False,
                is_influencer_video=False
            )
        
        # Video found - ALWAYS sync videos first to get fresh URLs
        print(f"[DEBUG] Sincronizando vídeos para {video.eldorado_username} antes da transcrição...")
        try:
            scraptik = ScrapTikService()
            sponsored_videos = scraptik.get_eldorado_videos(video.tiktok_username)
            
            # Update the specific video with fresh URLs if found
            for video_data in sponsored_videos:
                if video_data['tiktok_video_id'] == video.tiktok_video_id:
                    video.watermark_free_url = video_data['watermark_free_url']
                    video.watermark_free_url_alt1 = video_data.get('watermark_free_url_alt1')
                    video.watermark_free_url_alt2 = video_data.get('watermark_free_url_alt2')
                    db.commit()
                    print(f"[DEBUG] URLs atualizados para vídeo {video.tiktok_video_id}")
                    break
        except Exception as sync_error:
            print(f"[DEBUG] Erro na sincronização prévia: {sync_error}")
            # Continue mesmo se a sincronização falhar
        
        # Refresh video object to get updated URLs
        db.refresh(video)
        
        if not video.watermark_free_url:
            return VideoTranscriptionResponse(
                success=False,
                message="URL do vídeo sem marca d'água não disponível mesmo após sincronização.",
                video_found=True,
                is_influencer_video=True,
                eldorado_username=video.eldorado_username
            )
        
        # Check if transcription already exists
        if video.transcription:
            return VideoTranscriptionResponse(
                success=True,
                message="Transcrição já existe (cache)!",
                video_found=True,
                is_influencer_video=True,
                eldorado_username=video.eldorado_username,
                transcription=video.transcription,
                video_info=TikTokVideoResponse.model_validate(video)
            )
        
        # Transcribe video using OpenAI
        openai_service = OpenAIService()
        
        try:
            # Try multiple URLs in cascata: primary, alt1, alt2
            transcription = None
            urls_to_try = []
            
            # Build list of URLs to try in order
            if video.watermark_free_url:
                urls_to_try.append(("primary", video.watermark_free_url))
            if hasattr(video, 'watermark_free_url_alt1') and video.watermark_free_url_alt1:
                urls_to_try.append(("alt1", video.watermark_free_url_alt1))
            if hasattr(video, 'watermark_free_url_alt2') and video.watermark_free_url_alt2:
                urls_to_try.append(("alt2", video.watermark_free_url_alt2))
            
            print(f"[DEBUG] Testando {len(urls_to_try)} URLs em cascata...")
            
            last_error = None
            errors_by_url = {}
            
            for url_type, video_url in urls_to_try:
                try:
                    print(f"[DEBUG] Tentando URL {url_type}: {video_url[:50]}...")
                    transcription = openai_service.transcribe_from_url(video_url)
                    print(f"[DEBUG] SUCESSO com URL {url_type}!")
                    break  # Success, exit loop
                    
                except Exception as url_error:
                    error_msg = str(url_error)
                    print(f"[DEBUG] FALHA com URL {url_type}: {error_msg}")
                    errors_by_url[url_type] = error_msg
                    last_error = url_error
                    continue  # Try next URL
            
            # If we get here without transcription, ALL URLs failed
            if transcription is None:
                # Create detailed error message showing all failed attempts
                error_details = []
                for url_type, error_msg in errors_by_url.items():
                    error_details.append(f"{url_type}: {error_msg}")
                
                detailed_error = f"Todos os {len(urls_to_try)} URLs falharam:\n" + "\n".join(error_details)
                print(f"[DEBUG] {detailed_error}")
                
                # Return comprehensive error response
                return VideoTranscriptionResponse(
                    success=False,
                    message=f"Não foi possível transcrever o vídeo. Todos os URLs falharam mesmo após sincronização. Últimos erros: {'; '.join([f'{k}={v}' for k, v in errors_by_url.items()])}",
                    video_found=True,
                    is_influencer_video=True,
                    eldorado_username=video.eldorado_username
                )
            
            # Save transcription to database
            video.transcription = transcription
            db.commit()
            
            return VideoTranscriptionResponse(
                success=True,
                message="Transcrição realizada com sucesso!",
                video_found=True,
                is_influencer_video=True,
                eldorado_username=video.eldorado_username,
                transcription=transcription,
                video_info=TikTokVideoResponse.model_validate(video)
            )
            
        except Exception as e:
            return VideoTranscriptionResponse(
                success=False,
                message=f"Erro na transcrição: {str(e)}",
                video_found=True,
                is_influencer_video=True,
                eldorado_username=video.eldorado_username
            )
    
    except Exception as e:
        return VideoTranscriptionResponse(
            success=False,
            message=f"Erro interno: {str(e)}"
        )