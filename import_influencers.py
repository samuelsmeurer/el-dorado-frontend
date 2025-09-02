#!/usr/bin/env python3
import csv
import requests
import json
from typing import List, Dict

def read_csv_data(file_path: str) -> List[Dict[str, str]]:
    """Read influencers data from CSV file"""
    influencers = []
    
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            influencers.append({
                'first_name': row['Nome'],
                'eldorado_username': row['Nome'],  # Using Nome as eldorado_username
                'tiktok_username': row['tiktok @'],
                'country': row['Pais'],
                'owner': row['Owner'],
                'phone': row['telefone'] if row['telefone'] != 'null' else None
            })
    
    return influencers

def create_influencer(influencer_data: Dict[str, str], api_base_url: str) -> Dict:
    """Create an influencer using the API"""
    url = f"{api_base_url}/api/v1/influencers/"
    
    # Prepare payload
    payload = {
        'first_name': influencer_data['first_name'],
        'eldorado_username': influencer_data['eldorado_username'],
        'country': influencer_data['country'],
        'owner': influencer_data['owner']
    }
    
    # Add optional fields
    if influencer_data.get('tiktok_username'):
        payload['tiktok_username'] = influencer_data['tiktok_username']
    
    if influencer_data.get('phone'):
        payload['phone'] = influencer_data['phone']
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return {
            'success': True,
            'data': response.json(),
            'status_code': response.status_code
        }
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': str(e),
            'status_code': response.status_code if 'response' in locals() else None,
            'response_text': response.text if 'response' in locals() else None
        }

def import_all_influencers(csv_file_path: str, api_base_url: str = "http://localhost:8000"):
    """Import all influencers from CSV to database via API"""
    
    print(f"Reading influencers from {csv_file_path}...")
    influencers = read_csv_data(csv_file_path)
    print(f"Found {len(influencers)} influencers to import")
    
    success_count = 0
    error_count = 0
    errors = []
    
    for i, influencer in enumerate(influencers, 1):
        print(f"\n[{i}/{len(influencers)}] Creating influencer: {influencer['eldorado_username']}")
        
        result = create_influencer(influencer, api_base_url)
        
        if result['success']:
            success_count += 1
            print(f"✅ Successfully created: {influencer['eldorado_username']}")
        else:
            error_count += 1
            error_msg = f"❌ Failed to create {influencer['eldorado_username']}: {result['error']}"
            print(error_msg)
            errors.append({
                'influencer': influencer['eldorado_username'],
                'error': result['error'],
                'status_code': result.get('status_code'),
                'response': result.get('response_text')
            })
    
    # Summary
    print(f"\n{'='*50}")
    print(f"IMPORT SUMMARY")
    print(f"{'='*50}")
    print(f"Total influencers: {len(influencers)}")
    print(f"Successfully created: {success_count}")
    print(f"Failed: {error_count}")
    
    if errors:
        print(f"\n{'='*50}")
        print(f"ERRORS:")
        print(f"{'='*50}")
        for error in errors:
            print(f"- {error['influencer']}: {error['error']}")
            if error.get('response'):
                print(f"  Response: {error['response']}")

if __name__ == "__main__":
    import sys
    
    # Default values
    csv_file = "influencers_limpo.csv"
    api_url = "http://localhost:8000"
    
    # Allow command line arguments
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    if len(sys.argv) > 2:
        api_url = sys.argv[2]
    
    print(f"Starting import process...")
    print(f"CSV file: {csv_file}")
    print(f"API URL: {api_url}")
    
    import_all_influencers(csv_file, api_url)