# SmashRanking
A smash discord bot that manages smash games between friends!

# Key Features
- Player elo leaderboard that follows chess elo algorithm
- Register games between players
- Display statistical insights on match histories, played characters and specific player matchups

# Setup
To install the necessary libraries run the command
```
pip install -r requirements.txt
```

The following environment variables must be defined for a PostgreSQL database
```
DB_USERNAME
DB_PASSWORD
DB_HOST
DB_PORT
DB_NAME
```

The following environment variables must be defined for discord.py
```
BOT_TOKEN
```

To run the bot, execute the following command
```
python3 main.py
```
