from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, extract
from typing import List, Optional
from datetime import datetime, date
from ..core.database import get_db
from ..models import Influencer, TikTokVideo
from ..schemas import TopVideo, InfluencerStats, DashboardStats

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get general dashboard statistics"""
    
    # Total counts
    total_influencers = db.query(Influencer).filter(Influencer.status == "active").count()
    total_videos = db.query(TikTokVideo).count()
    
    # Sum metrics
    metrics = db.query(
        func.sum(TikTokVideo.view_count).label("total_views"),
        func.sum(TikTokVideo.like_count).label("total_likes"),
        func.avg(
            (TikTokVideo.like_count + TikTokVideo.comment_count + TikTokVideo.share_count) /
            func.nullif(TikTokVideo.view_count, 0) * 100
        ).label("avg_engagement")
    ).first()
    
    # Videos this month
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    videos_this_month = db.query(TikTokVideo).filter(
        extract("month", TikTokVideo.published_at) == current_month,
        extract("year", TikTokVideo.published_at) == current_year
    ).count()
    
    return DashboardStats(
        total_influencers=total_influencers,
        total_videos=total_videos,
        total_views=metrics.total_views or 0,
        total_likes=metrics.total_likes or 0,
        avg_engagement_rate=round(metrics.avg_engagement or 0.0, 2),
        videos_this_month=videos_this_month
    )


@router.get("/top-videos/likes", response_model=List[TopVideo])
def get_top_videos_by_likes(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get top videos by like count"""
    
    videos = db.query(
        TikTokVideo.eldorado_username,
        TikTokVideo.tiktok_username,
        TikTokVideo.tiktok_video_id,
        TikTokVideo.description,
        TikTokVideo.like_count.label("metric_value"),
        TikTokVideo.published_at
    ).order_by(desc(TikTokVideo.like_count)).limit(limit).all()
    
    return [
        TopVideo(
            eldorado_username=video.eldorado_username,
            tiktok_username=video.tiktok_username,
            tiktok_video_id=video.tiktok_video_id,
            description=video.description or "",
            metric_value=video.metric_value,
            published_at=video.published_at
        )
        for video in videos
    ]


@router.get("/top-videos/views", response_model=List[TopVideo])
def get_top_videos_by_views(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get top videos by view count"""
    
    videos = db.query(
        TikTokVideo.eldorado_username,
        TikTokVideo.tiktok_username,
        TikTokVideo.tiktok_video_id,
        TikTokVideo.description,
        TikTokVideo.view_count.label("metric_value"),
        TikTokVideo.published_at
    ).order_by(desc(TikTokVideo.view_count)).limit(limit).all()
    
    return [
        TopVideo(
            eldorado_username=video.eldorado_username,
            tiktok_username=video.tiktok_username,
            tiktok_video_id=video.tiktok_video_id,
            description=video.description or "",
            metric_value=video.metric_value,
            published_at=video.published_at
        )
        for video in videos
    ]


@router.get("/top-videos/engagement", response_model=List[TopVideo])
def get_top_videos_by_engagement(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get top videos by engagement rate"""
    
    videos = db.query(
        TikTokVideo.eldorado_username,
        TikTokVideo.tiktok_username,
        TikTokVideo.tiktok_video_id,
        TikTokVideo.description,
        ((TikTokVideo.like_count + TikTokVideo.comment_count + TikTokVideo.share_count) /
         func.nullif(TikTokVideo.view_count, 0) * 100).label("metric_value"),
        TikTokVideo.published_at
    ).filter(
        TikTokVideo.view_count > 0
    ).order_by(
        desc("metric_value")
    ).limit(limit).all()
    
    return [
        TopVideo(
            eldorado_username=video.eldorado_username,
            tiktok_username=video.tiktok_username,
            tiktok_video_id=video.tiktok_video_id,
            description=video.description or "",
            metric_value=int(video.metric_value or 0),
            published_at=video.published_at
        )
        for video in videos
    ]


@router.get("/influencer/{eldorado_username}", response_model=InfluencerStats)
def get_influencer_stats(
    eldorado_username: str,
    db: Session = Depends(get_db)
):
    """Get statistics for a specific influencer"""
    
    # Check if influencer exists
    influencer = db.query(Influencer).filter(
        Influencer.eldorado_username == eldorado_username
    ).first()
    
    if not influencer:
        raise HTTPException(
            status_code=404,
            detail=f"Influencer '{eldorado_username}' not found"
        )
    
    # Get video statistics
    stats = db.query(
        func.count(TikTokVideo.id).label("total_videos"),
        func.avg(TikTokVideo.like_count).label("avg_likes"),
        func.avg(TikTokVideo.view_count).label("avg_views"),
        func.max(TikTokVideo.view_count).label("best_performance"),
        func.max(TikTokVideo.published_at).label("last_video_date")
    ).filter(
        TikTokVideo.eldorado_username == eldorado_username
    ).first()
    
    return InfluencerStats(
        eldorado_username=eldorado_username,
        total_videos=stats.total_videos or 0,
        avg_likes=round(stats.avg_likes or 0.0, 2),
        avg_views=round(stats.avg_views or 0.0, 2),
        best_performance=stats.best_performance or 0,
        last_video_date=stats.last_video_date
    )


@router.get("/period")
def get_period_stats(
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """Get statistics for a specific period"""
    
    if start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="Start date must be before end date"
        )
    
    # Videos in period
    videos = db.query(TikTokVideo).filter(
        TikTokVideo.published_at >= start_date,
        TikTokVideo.published_at <= end_date
    ).all()
    
    if not videos:
        return {
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "total_videos": 0,
            "total_views": 0,
            "total_likes": 0,
            "avg_engagement": 0.0,
            "active_influencers": 0
        }
    
    total_videos = len(videos)
    total_views = sum(v.view_count for v in videos)
    total_likes = sum(v.like_count for v in videos)
    total_interactions = sum(v.like_count + v.comment_count + v.share_count for v in videos)
    
    avg_engagement = (total_interactions / total_views * 100) if total_views > 0 else 0.0
    active_influencers = len(set(v.eldorado_username for v in videos))
    
    return {
        "period": {
            "start_date": start_date,
            "end_date": end_date
        },
        "total_videos": total_videos,
        "total_views": total_views,
        "total_likes": total_likes,
        "avg_engagement": round(avg_engagement, 2),
        "active_influencers": active_influencers
    }


@router.get("/monthly-summary")
def get_monthly_summary(
    months: int = Query(6, ge=1, le=24, description="Number of months to include"),
    db: Session = Depends(get_db)
):
    """Get monthly summary of video performance"""
    
    monthly_data = db.query(
        func.date_trunc('month', TikTokVideo.published_at).label('month'),
        func.count(TikTokVideo.id).label('total_videos'),
        func.avg(TikTokVideo.view_count).label('avg_views'),
        func.sum(TikTokVideo.like_count).label('total_likes'),
        func.count(func.distinct(TikTokVideo.eldorado_username)).label('active_influencers')
    ).filter(
        TikTokVideo.published_at >= func.date_trunc('month', func.now()) - func.make_interval(months=months)
    ).group_by(
        func.date_trunc('month', TikTokVideo.published_at)
    ).order_by(
        func.date_trunc('month', TikTokVideo.published_at)
    ).all()
    
    return {
        "summary": [
            {
                "month": row.month.strftime("%Y-%m") if row.month else None,
                "total_videos": row.total_videos,
                "avg_views": round(row.avg_views or 0.0, 2),
                "total_likes": row.total_likes or 0,
                "active_influencers": row.active_influencers
            }
            for row in monthly_data
        ]
    }