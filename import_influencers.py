#!/usr/bin/env python3
"""
Script to import influencers from CSV file to the database
"""
import csv
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.influencer import Influencer, OwnerType
from app.core.database import Base

# Database configuration
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/el_dorado_db"

def create_db_session():
    """Create database session"""
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal(), engine

def import_influencers_from_csv(csv_file_path):
    """Import influencers from CSV file"""
    session, engine = create_db_session()
    
    try:
        # Read CSV file
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            imported_count = 0
            skipped_count = 0
            errors = []
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 because of header
                try:
                    # Clean up data
                    nome = row['Nome'].strip()
                    eldorado_username = row['User El dorado'].strip()
                    tiktok_username = row['tiktok @'].strip()
                    pais = row['Pais'].strip() if row['Pais'].strip() else None
                    owner_str = row['Owner'].strip().lower()
                    
                    # Skip if essential data is missing
                    if not nome or not eldorado_username:
                        skipped_count += 1
                        errors.append(f"Row {row_num}: Missing essential data (nome or eldorado_username)")
                        continue
                    
                    # Check if influencer already exists
                    existing = session.query(Influencer).filter_by(eldorado_username=eldorado_username).first()
                    if existing:
                        skipped_count += 1
                        errors.append(f"Row {row_num}: Influencer {eldorado_username} already exists")
                        continue
                    
                    # Validate owner
                    try:
                        owner_enum = OwnerType(owner_str)
                    except ValueError:
                        skipped_count += 1
                        errors.append(f"Row {row_num}: Invalid owner '{owner_str}' for {eldorado_username}")
                        continue
                    
                    # Create new influencer
                    influencer = Influencer(
                        first_name=nome,
                        eldorado_username=eldorado_username,
                        phone=None,  # Set as null as specified
                        country=pais,
                        owner=owner_enum,
                        status="active"
                    )
                    
                    session.add(influencer)
                    imported_count += 1
                    print(f"✅ Added: {eldorado_username} ({nome}) - Owner: {owner_str}")
                    
                except Exception as e:
                    skipped_count += 1
                    error_msg = f"Row {row_num}: Error processing {row.get('User El dorado', 'unknown')}: {str(e)}"
                    errors.append(error_msg)
                    print(f"❌ {error_msg}")
                    continue
            
            # Commit all changes
            session.commit()
            print(f"\n🎉 Import completed!")
            print(f"✅ Successfully imported: {imported_count} influencers")
            print(f"⏭️  Skipped: {skipped_count} entries")
            
            if errors:
                print(f"\n⚠️  Errors encountered:")
                for error in errors[:10]:  # Show first 10 errors
                    print(f"   {error}")
                if len(errors) > 10:
                    print(f"   ... and {len(errors) - 10} more errors")
                    
    except Exception as e:
        session.rollback()
        print(f"💥 Fatal error: {str(e)}")
        return False
    finally:
        session.close()
        
    return True

def main():
    csv_file = "/Users/samuelschramm/Downloads/influencers_limpo.csv"
    
    if not os.path.exists(csv_file):
        print(f"❌ CSV file not found: {csv_file}")
        return
        
    print(f"🚀 Starting import from: {csv_file}")
    print(f"📊 Database: {DATABASE_URL}")
    print("-" * 60)
    
    success = import_influencers_from_csv(csv_file)
    
    if success:
        print("\n✅ Import process completed successfully!")
    else:
        print("\n❌ Import process failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
