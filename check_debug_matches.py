#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/ubuntu/CodeRoad/backend')

from app.core.database import SessionLocal
from app.models.match import Match
from sqlalchemy import desc

db = SessionLocal()
matches = db.query(Match).filter(Match.challenge_type == 'debug').order_by(desc(Match.created_at)).limit(5).all()

print('=== Recent Debug Arena Matches ===\n')
for m in matches:
    print(f'Match ID: {m.id}')
    print(f'Created: {m.created_at}')
    print(f'Challenge Title: {m.challenge_title}')
    print(f'Challenge Description (first 200 chars):')
    print(f'  {m.challenge_description[:200] if m.challenge_description else "None"}...')
    print(f'Buggy Code (first 150 chars):')
    print(f'  {m.buggy_code[:150] if m.buggy_code else "None"}...')
    print(f'Status: {m.status}')
    print('-' * 80)

db.close()
