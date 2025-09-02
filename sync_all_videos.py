#!/usr/bin/env python3
import requests
import time
import json
import psycopg2
from typing import Dict, List

API_BASE_URL = "http://localhost:8000"
DATABASE_URL = "postgresql://postgres:PLLfLHcQoBSLlPmsQLRytEtDOmBQptwi@yamanote.proxy.rlwy.net:28818/railway"

def get_influencers_with_tiktok_id() -> List[Dict]:
    """Get all influencers that have TikTok ID (not NULL)"""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    query = """
    SELECT eldorado_username, tiktok_username, tiktok_id 
    FROM influencer_ids 
    WHERE tiktok_id IS NOT NULL 
    AND tiktok_id != ''
    ORDER BY eldorado_username;
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return [{
        "eldorado_username": row[0], 
        "tiktok_username": row[1], 
        "tiktok_id": row[2]
    } for row in results]

def sync_influencer_videos(eldorado_username: str) -> Dict:
    """Sync videos for a specific influencer using the API"""
    try:
        url = f"{API_BASE_URL}/api/v1/videos/sync/{eldorado_username}"
        response = requests.post(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'data': data
            }
        else:
            return {
                'success': False,
                'error': response.text,
                'status_code': response.status_code
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def sync_all_videos():
    """Sync videos for all influencers with TikTok ID"""
    
    print("🔍 Buscando influenciadores com TikTok ID...")
    influencers = get_influencers_with_tiktok_id()
    
    if not influencers:
        print("❌ Nenhum influenciador encontrado com TikTok ID!")
        return
    
    print(f"📊 Encontrados {len(influencers)} influenciadores com TikTok ID")
    print("🚀 Iniciando sincronização de vídeos...")
    
    results = []
    success_count = 0
    error_count = 0
    total_videos = 0
    total_new_videos = 0
    total_updated_videos = 0
    
    for i, influencer in enumerate(influencers, 1):
        username = influencer['eldorado_username']
        tiktok_username = influencer['tiktok_username']
        tiktok_id = influencer['tiktok_id']
        
        print(f"\n[{i}/{len(influencers)}] Sincronizando vídeos: {username}")
        print(f"  TikTok: @{tiktok_username} (ID: {tiktok_id})")
        
        result = sync_influencer_videos(username)
        
        if result['success']:
            data = result['data']
            videos_processed = data.get('videos_processed', 0)
            new_videos = data.get('new_videos', 0)
            updated_videos = data.get('updated_videos', 0)
            
            print(f"  ✅ Sucesso!")
            print(f"    - Vídeos processados: {videos_processed}")
            print(f"    - Novos vídeos: {new_videos}")
            print(f"    - Vídeos atualizados: {updated_videos}")
            
            results.append({
                'eldorado_username': username,
                'tiktok_username': tiktok_username,
                'tiktok_id': tiktok_id,
                'status': 'success',
                'videos_processed': videos_processed,
                'new_videos': new_videos,
                'updated_videos': updated_videos,
                'response': data
            })
            
            success_count += 1
            total_videos += videos_processed
            total_new_videos += new_videos
            total_updated_videos += updated_videos
            
        else:
            print(f"  ❌ Erro: {result['error']}")
            results.append({
                'eldorado_username': username,
                'tiktok_username': tiktok_username,
                'tiktok_id': tiktok_id,
                'status': 'failed',
                'error': result['error'],
                'status_code': result.get('status_code')
            })
            error_count += 1
        
        # Delay to avoid overwhelming the API
        if i < len(influencers):
            time.sleep(2)  # 2 seconds delay between requests
    
    # Summary
    print(f"\n{'='*70}")
    print(f"📈 RESUMO FINAL DA SINCRONIZAÇÃO")
    print(f"{'='*70}")
    print(f"Total de influenciadores processados: {len(influencers)}")
    print(f"Sucessos: {success_count}")
    print(f"Erros: {error_count}")
    print(f"")
    print(f"📹 ESTATÍSTICAS DE VÍDEOS:")
    print(f"Total de vídeos processados: {total_videos}")
    print(f"Novos vídeos adicionados: {total_new_videos}")
    print(f"Vídeos atualizados: {total_updated_videos}")
    print(f"{'='*70}")
    
    # Save detailed results
    with open('video_sync_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"📁 Resultados detalhados salvos em: video_sync_results.json")
    
    # Show errors summary
    errors = [r for r in results if r['status'] == 'failed']
    if errors:
        print(f"\n❌ ERROS ENCONTRADOS ({len(errors)}):")
        for error in errors[:10]:  # Show first 10 errors
            print(f"  - {error['eldorado_username']}: {error['error']}")
        if len(errors) > 10:
            print(f"  ... e mais {len(errors) - 10} erros (veja video_sync_results.json)")

if __name__ == "__main__":
    print("🎬 Sincronização de Vídeos TikTok - El Dorado API")
    print("=" * 70)
    sync_all_videos()