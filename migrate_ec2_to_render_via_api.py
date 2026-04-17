#!/usr/bin/env python3
"""
Migrate data from EC2 to Render by pulling via API and pushing to Render
"""
import requests
import sys

EC2_URL = "http://100.48.103.123:8000"
RENDER_URL = "https://coderoad-gmq6.onrender.com"

def get_all_players_from_ec2():
    """Get all players from EC2"""
    print("Fetching players from EC2...")
    response = requests.get(f"{EC2_URL}/api/v1/leaderboard/global?limit=1000")
    
    if response.status_code != 200:
        print(f"❌ Failed to get players: {response.status_code}")
        return []
    
    data = response.json()
    players = data.get('leaderboard', [])
    print(f"✅ Found {len(players)} players on EC2\n")
    return players

def migrate_players_to_render(players):
    """Migrate players to Render"""
    if not players:
        print("No players to migrate")
        return
    
    print(f"Migrating {len(players)} players to Render...")
    
    # We need to get full player data, not just leaderboard data
    # The leaderboard only has partial info
    # We'll need to register them or insert directly
    
    print("\n⚠️  Note: Leaderboard API only provides partial player data.")
    print("We need direct database access to migrate passwords and full profiles.")
    print("\nOptions:")
    print("1. SSH into EC2 and download the database file")
    print("2. Create a database export endpoint on EC2")
    print("3. Use AWS Systems Manager Session Manager")
    
    return

if __name__ == "__main__":
    players = get_all_players_from_ec2()
    migrate_players_to_render(players)
