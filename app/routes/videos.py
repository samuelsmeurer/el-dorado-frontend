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
                        existing_video.view_count = video_data['view_count']
                        existing_video.like_count = video_data['like_count']
                        existing_video.comment_count = video_data['comment_count']
                        existing_video.share_count = video_data['share_count']
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
        
        # Video found and it's from an influencer
        if not video.watermark_free_url:
            return VideoTranscriptionResponse(
                success=False,
                message="URL do vídeo sem marca d'água não disponível.",
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
            # Try multiple URLs in order: primary, alt1, alt2
            transcription = None
            urls_to_try = [("primary", video.watermark_free_url)]
            
            # Add alternative URLs if they exist (columns may not exist yet)
            try:
                if hasattr(video, 'watermark_free_url_alt1') and video.watermark_free_url_alt1:
                    urls_to_try.append(("alt1", video.watermark_free_url_alt1))
                if hasattr(video, 'watermark_free_url_alt2') and video.watermark_free_url_alt2:
                    urls_to_try.append(("alt2", video.watermark_free_url_alt2))
            except Exception as e:
                print(f"[DEBUG] Colunas alternativas ainda não existem: {e}")
                print(f"[DEBUG] Usando apenas URL principal por enquanto")
            
            last_error = None
            for url_type, video_url in urls_to_try:
                if not video_url:  # Skip if URL is None
                    continue
                    
                try:
                    print(f"[DEBUG] Tentando URL {url_type}: {video_url[:50]}...")
                    transcription = openai_service.transcribe_from_url(video_url)
                    print(f"[DEBUG] Sucesso com URL {url_type}!")
                    break  # Success, exit loop
                    
                except Exception as url_error:
                    print(f"[DEBUG] Falha com URL {url_type}: {str(url_error)}")
                    last_error = url_error
                    continue  # Try next URL
            
            # If we get here without transcription, all URLs failed
            if transcription is None:
                # If we get 403, try to sync videos to get fresh URLs
                if last_error and "403" in str(last_error):
                    print(f"[DEBUG] Todos URLs falharam com 403, tentando sincronizar...")
                    try:
                        # Call sync videos for this influencer  
                        from ..services.tiktok_service import TikTokService
                        tiktok_service = TikTokService()
                        sync_result = tiktok_service.sync_videos_for_influencer(video.eldorado_username)
                        print(f"[DEBUG] Sync concluído: {sync_result}")
                        
                        # Refresh video and try primary URL again
                        db.refresh(video)
                        if video.watermark_free_url:
                            transcription = openai_service.transcribe_from_url(video.watermark_free_url)
                        else:
                            raise Exception("URLs expiraram após sincronização. Tente novamente em alguns minutos.")
                    except Exception as sync_error:
                        print(f"[DEBUG] Erro na sincronização: {sync_error}")
                        raise Exception("URLs expiraram e não foi possível sincronizar. Tente novamente em alguns minutos.")
                else:
                    # Non-403 error, raise the last error
                    raise last_error
            
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