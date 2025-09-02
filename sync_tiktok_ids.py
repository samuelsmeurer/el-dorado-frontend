#!/usr/bin/env python3
import requests
import time
import json
from typing import List

API_BASE_URL = "http://localhost:8000"

def get_influencers_without_tiktok_id() -> List[str]:
    """Get list of influencers that don't have TikTok ID yet"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/influencers/", params={"limit": 200})
        response.raise_for_status()
        
        influencers = response.json()
        without_ids = []
        
        for influencer in influencers:
            # Get social IDs for this influencer
            username = influencer['eldorado_username']
            social_response = requests.get(f"{API_BASE_URL}/api/v1/influencers/{username}/social-ids")
            
            if social_response.status_code == 200:
                social_data = social_response.json()
                # If has TikTok username but no TikTok ID, add to list
                if social_data.get('tiktok_username') and not social_data.get('tiktok_id'):
                    without_ids.append(username)
        
        return without_ids
        
    except Exception as e:
        print(f"Error getting influencers: {e}")
        return []

def sync_tiktok_id(eldorado_username: str) -> dict:
    """Sync TikTok ID for a specific influencer"""
    try:
        url = f"{API_BASE_URL}/api/v1/influencers/{eldorado_username}/sync-tiktok-id"
        response = requests.post(url)
        
        if response.status_code == 200:
            return {
                'success': True,
                'data': response.json()
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

def sync_all_tiktok_ids():
    """Sync TikTok IDs for all influencers that don't have them"""
    print("🔍 Buscando influenciadores sem TikTok ID...")
    
    without_ids = get_influencers_without_tiktok_id()
    
    if not without_ids:
        print("✅ Todos os influenciadores já possuem TikTok ID!")
        return
    
    print(f"📊 Encontrados {len(without_ids)} influenciadores sem TikTok ID")
    print(f"🚀 Iniciando sincronização...")
    
    success_count = 0
    error_count = 0
    errors = []
    
    for i, username in enumerate(without_ids, 1):
        print(f"\n[{i}/{len(without_ids)}] Sincronizando: {username}")
        
        result = sync_tiktok_id(username)
        
        if result['success']:
            success_count += 1
            data = result['data']
            print(f"  ✅ Sucesso! TikTok ID: {data.get('tiktok_id', 'N/A')}")
        else:
            error_count += 1
            error_msg = f"❌ Erro: {result.get('error', 'Unknown error')}"
            print(f"  {error_msg}")
            errors.append({
                'username': username,
                'error': result.get('error'),
                'status_code': result.get('status_code')
            })
        
        # Wait between requests to avoid rate limiting
        if i < len(without_ids):
            time.sleep(1)  # 1 second delay between requests
    
    # Summary
    print(f"\n{'='*60}")
    print(f"RESUMO DA SINCRONIZAÇÃO")
    print(f"{'='*60}")
    print(f"Total processados: {len(without_ids)}")
    print(f"Sucessos: {success_count}")
    print(f"Erros: {error_count}")
    
    if errors:
        print(f"\n{'='*60}")
        print(f"ERROS ENCONTRADOS:")
        print(f"{'='*60}")
        for error in errors[:10]:  # Show first 10 errors
            print(f"- {error['username']}: {error['error']}")
        if len(errors) > 10:
            print(f"... e mais {len(errors) - 10} erros")

if __name__ == "__main__":
    print("🎯 Sincronização de TikTok IDs - El Dorado API")
    print("=" * 50)
    sync_all_tiktok_ids()