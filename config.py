from decouple import config

bot_token = config('BOT_TOKEN')
postgres_password = config('POSTGRES_PASSWORD')
db_url = f"postgresql://postgres:{postgres_password}@postgres_bot/postgres"