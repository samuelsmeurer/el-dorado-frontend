from openai import OpenAI
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from ..core.config import settings
from ..models import Influencer, TikTokVideo, Owner, InfluencerIds
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import json


class ElDoradoAIAssistant:
    """AI Assistant com contexto da El Dorado e acesso aos dados dos influenciadores"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.company_context = self._get_company_context()
    
    def _get_company_context(self) -> str:
        """Contexto base da empresa El Dorado"""
        return """
        Você é o assistente AI oficial da El Dorado P2P, uma empresa de marketing de influenciadores especializada em TikTok.
        
        CONTEXTO DA EMPRESA:
        - El Dorado P2P trabalha com influenciadores no TikTok para promover produtos P2P
        - Focamos em vídeos patrocinados que mencionam "@El Dorado P2P"
        - Temos uma equipe de recrutamento com os seguintes responsáveis:
          * Alejandra, Alessandro, Bianca, Camilo, Jesus, Julia, Samuel
        - Medimos engagement através de likes, views, comments e shares
        - Engagement Rate = (Likes + Comments + Shares) / Views * 100
        
        DADOS DISPONÍVEIS:
        - Influenciadores cadastrados com seus responsáveis (owners)
        - Vídeos patrocinados do TikTok com métricas completas
        - Transcrições dos vídeos (quando disponíveis)
        - Analytics de performance por influenciador e período
        
        SUAS CAPACIDADES:
        - Responder perguntas sobre performance de influenciadores
        - Fornecer insights sobre campanhas e métricas
        - Analisar tendências de engagement
        - Sugerir melhorias baseadas em dados
        - Comparar performance entre influenciadores e períodos
        
        IMPORTANTE: Sempre forneça respostas baseadas em dados reais do banco. Se não tiver dados suficientes, seja transparente sobre isso.
        """
    
    def _get_database_summary(self, db: Session) -> Dict[str, Any]:
        """Obter resumo atual do banco de dados"""
        try:
            # Stats básicas
            total_influencers = db.query(Influencer).filter(Influencer.status == "active").count()
            total_videos = db.query(TikTokVideo).count()
            
            # Videos este mês
            start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            videos_this_month = db.query(TikTokVideo).filter(TikTokVideo.created_at >= start_of_month).count()
            
            # Total de métricas
            total_views = db.query(func.sum(TikTokVideo.view_count)).scalar() or 0
            total_likes = db.query(func.sum(TikTokVideo.like_count)).scalar() or 0
            
            # Top performers
            top_videos = db.query(TikTokVideo)\
                .order_by(desc(TikTokVideo.like_count))\
                .limit(5)\
                .all()
            
            # Influenciadores por owner
            owners_stats = db.query(
                Influencer.owner, 
                func.count(Influencer.id).label('count')
            ).filter(Influencer.status == "active")\
             .group_by(Influencer.owner)\
             .all()
            
            return {
                "total_influencers": total_influencers,
                "total_videos": total_videos,
                "videos_this_month": videos_this_month,
                "total_views": total_views,
                "total_likes": total_likes,
                "top_videos": [
                    {
                        "eldorado_username": video.eldorado_username,
                        "likes": video.like_count,
                        "views": video.view_count
                    } for video in top_videos
                ],
                "owners_distribution": [
                    {"owner": owner.value, "count": count} 
                    for owner, count in owners_stats
                ]
            }
        except Exception as e:
            return {"error": f"Erro ao obter dados: {str(e)}"}
    
    def _search_influencers(self, db: Session, query_terms: List[str]) -> List[Dict]:
        """Buscar influenciadores baseado em termos de pesquisa"""
        try:
            query = db.query(Influencer).filter(Influencer.status == "active")
            
            for term in query_terms:
                query = query.filter(
                    (Influencer.first_name.ilike(f"%{term}%")) |
                    (Influencer.eldorado_username.ilike(f"%{term}%")) |
                    (Influencer.owner == term.lower())
                )
            
            influencers = query.limit(10).all()
            
            result = []
            for inf in influencers:
                # Get video stats
                video_stats = db.query(
                    func.count(TikTokVideo.id).label('total_videos'),
                    func.avg(TikTokVideo.like_count).label('avg_likes'),
                    func.avg(TikTokVideo.view_count).label('avg_views'),
                    func.max(TikTokVideo.created_at).label('last_video')
                ).filter(TikTokVideo.eldorado_username == inf.eldorado_username).first()
                
                result.append({
                    "eldorado_username": inf.eldorado_username,
                    "first_name": inf.first_name,
                    "owner": inf.owner.value,
                    "country": inf.country,
                    "total_videos": video_stats.total_videos or 0,
                    "avg_likes": round(video_stats.avg_likes or 0, 1),
                    "avg_views": round(video_stats.avg_views or 0, 1),
                    "last_video": video_stats.last_video
                })
            
            return result
        except Exception as e:
            return [{"error": f"Erro na busca: {str(e)}"}]
    
    def _search_video_transcriptions(self, db: Session, query_terms: List[str]) -> List[Dict]:
        """Buscar vídeos com transcrições baseado em termos de pesquisa"""
        try:
            # Primeiro, buscar todos os vídeos com transcrições
            base_query = db.query(TikTokVideo).filter(
                TikTokVideo.transcription.isnot(None),
                TikTokVideo.transcription != ""
            )
            
            # Se há termos de busca, filtrar por eles
            if query_terms:
                filter_conditions = []
                for term in query_terms:
                    filter_conditions.extend([
                        TikTokVideo.eldorado_username.ilike(f"%{term}%"),
                        TikTokVideo.transcription.ilike(f"%{term}%"),
                        TikTokVideo.description.ilike(f"%{term}%")
                    ])
                
                # Usar OR para combinar todas as condições
                from sqlalchemy import or_
                combined_filter = or_(*filter_conditions)
                base_query = base_query.filter(combined_filter)
            
            videos = base_query.order_by(desc(TikTokVideo.created_at)).limit(10).all()
            
            result = []
            for video in videos:
                result.append({
                    "eldorado_username": video.eldorado_username,
                    "tiktok_video_id": video.tiktok_video_id,
                    "description": video.description[:100] + "..." if video.description and len(video.description) > 100 else video.description,
                    "transcription": video.transcription[:300] + "..." if video.transcription and len(video.transcription) > 300 else video.transcription,
                    "likes": video.like_count,
                    "views": video.view_count,
                    "published_at": video.published_at,
                    "created_at": video.created_at
                })
            
            return result
        except Exception as e:
            return [{"error": f"Erro na busca de transcrições: {str(e)}"}]
    
    def _get_analytics_data(self, db: Session, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Obter dados de analytics com filtros opcionais"""
        try:
            query = db.query(TikTokVideo)
            
            # Aplicar filtros se fornecidos
            if filters:
                if "owner" in filters:
                    query = query.join(Influencer).filter(Influencer.owner == filters["owner"])
                if "days" in filters:
                    date_threshold = datetime.now() - timedelta(days=filters["days"])
                    query = query.filter(TikTokVideo.created_at >= date_threshold)
                if "eldorado_username" in filters:
                    query = query.filter(TikTokVideo.eldorado_username == filters["eldorado_username"])
            
            videos = query.all()
            
            if not videos:
                return {"message": "Nenhum vídeo encontrado com os filtros aplicados"}
            
            # Calcular métricas
            total_videos = len(videos)
            total_views = sum(v.view_count for v in videos)
            total_likes = sum(v.like_count for v in videos)
            total_comments = sum(v.comment_count for v in videos)
            total_shares = sum(v.share_count for v in videos)
            
            avg_engagement = ((total_likes + total_comments + total_shares) / total_views * 100) if total_views > 0 else 0
            
            # Top performers
            top_videos = sorted(videos, key=lambda x: x.like_count, reverse=True)[:5]
            
            return {
                "total_videos": total_videos,
                "total_views": total_views,
                "total_likes": total_likes,
                "avg_engagement_rate": round(avg_engagement, 2),
                "top_videos": [
                    {
                        "eldorado_username": v.eldorado_username,
                        "tiktok_video_id": v.tiktok_video_id,
                        "likes": v.like_count,
                        "views": v.view_count,
                        "description": v.description[:100] + "..." if v.description and len(v.description) > 100 else v.description
                    } for v in top_videos
                ]
            }
        except Exception as e:
            return {"error": f"Erro ao obter analytics: {str(e)}"}
    
    def process_user_message(self, message: str, db: Session) -> str:
        """Processar mensagem do usuário e gerar resposta contextualizada"""
        try:
            # Obter contexto atual do banco
            db_summary = self._get_database_summary(db)
            
            # Detectar intenção do usuário e buscar dados relevantes
            message_lower = message.lower()
            relevant_data = {}
            
            # Se pergunta sobre owner específico
            owners = ["alejandra", "alessandro", "bianca", "camilo", "jesus", "julia", "samuel"]
            for owner in owners:
                if owner in message_lower:
                    relevant_data["owner_analytics"] = self._get_analytics_data(db, {"owner": owner})
                    relevant_data["owner_influencers"] = self._search_influencers(db, [owner])
                    break
            
            # Se pergunta sobre transcrições
            if any(word in message_lower for word in ["transcri", "transcrição", "transcricao", "fala", "disse", "falou"]):
                # Extrair possíveis nomes para busca de transcrições
                words = message.split()
                search_terms = []
                for word in words:
                    if len(word) > 3 and word.lower() not in ["transcricao", "transcri", "transcrição", "videos", "vídeos", "mostra", "sobre"]:
                        search_terms.append(word)
                
                if search_terms:
                    found_transcriptions = self._search_video_transcriptions(db, search_terms)
                    if found_transcriptions and not (len(found_transcriptions) == 1 and found_transcriptions[0].get("error")):
                        relevant_data["video_transcriptions"] = found_transcriptions
                        
            # Se menciona algum influenciador específico
            elif any(word in message_lower for word in ["influencer", "usuário", "@"]):
                # Extrair possíveis nomes de usuário
                words = message.split()
                for word in words:
                    if len(word) > 3:  # Evitar palavras muito curtas
                        found_influencers = self._search_influencers(db, [word])
                        if found_influencers and not found_influencers[0].get("error"):
                            relevant_data["searched_influencers"] = found_influencers
                            break
            
            # Se pergunta sobre período específico
            if any(word in message_lower for word in ["mes", "mês", "semana", "dia", "último"]):
                if "semana" in message_lower:
                    relevant_data["recent_analytics"] = self._get_analytics_data(db, {"days": 7})
                elif "mes" in message_lower or "mês" in message_lower:
                    relevant_data["recent_analytics"] = self._get_analytics_data(db, {"days": 30})
            
            # Preparar prompt para o ChatGPT
            system_prompt = f"""
            {self.company_context}
            
            DADOS ATUAIS DO SISTEMA:
            {json.dumps(db_summary, indent=2, ensure_ascii=False, default=str)}
            
            DADOS RELEVANTES PARA A PERGUNTA:
            {json.dumps(relevant_data, indent=2, ensure_ascii=False, default=str)}
            
            Responda de forma natural, útil e baseada nos dados reais. Use emojis quando apropriado e seja conversacional mas profissional.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"❌ Desculpe, ocorreu um erro ao processar sua pergunta: {str(e)}"
    
    def get_suggestions(self, db: Session) -> List[str]:
        """Gerar sugestões de perguntas baseadas nos dados disponíveis"""
        suggestions = [
            "📊 Como está a performance geral este mês?",
            "🏆 Quais são os top 5 vídeos com mais likes?", 
            "👥 Quantos influenciadores cada owner tem?",
            "📈 Qual é a taxa de engagement média?",
            "🔍 Me mostra os stats do Samuel",
            "📹 Quantos vídeos foram postados esta semana?",
            "💬 Me mostra as transcrições da Andy Flores",
            "🎙️ Quais vídeos têm transcrições disponíveis?",
            "💡 Que insights você pode me dar sobre as campanhas?",
            "🎯 Quais influenciadores estão performando melhor?"
        ]
        return suggestions