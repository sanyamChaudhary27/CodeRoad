import requests

# Check how many players are on EC2
response = requests.get("http://100.48.103.123:8000/api/v1/leaderboard/global?limit=1000")

if response.status_code == 200:
    data = response.json()
    players = data.get('leaderboard', [])
    print(f"✅ Players on EC2: {len(players)}")
    print(f"\nFirst 10 players:")
    for i, player in enumerate(players[:10], 1):
        print(f"  {i}. {player.get('username')} (Rating: {player.get('current_rating')})")
else:
    print(f"❌ Error: {response.status_code} - {response.text}")
