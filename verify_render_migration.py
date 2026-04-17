import requests

# Check players on Render
response = requests.get("https://coderoad-gmq6.onrender.com/api/v1/leaderboard/global?limit=1000")

if response.status_code == 200:
    data = response.json()
    players = data.get('leaderboard', [])
    print(f"✅ Players on Render: {len(players)}")
    print(f"\nTop 10 players:")
    for i, player in enumerate(players[:10], 1):
        print(f"  {i}. {player.get('username')} (Rating: {player.get('current_rating')})")
else:
    print(f"❌ Error: {response.status_code}")
