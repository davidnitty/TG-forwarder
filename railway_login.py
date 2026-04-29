# railway_login.py
import asyncio
from telethon import TelegramClient
from dotenv import load_dotenv
import os

load_dotenv()

async def main():
    print("🔐 Railway Authentication")
    print("=" * 60)
    
    client = TelegramClient(
        'forwarder_session',
        int(os.getenv('API_ID')),
        os.getenv('API_HASH')
    )
    
    await client.start(phone=os.getenv('PHONE'))
    me = await client.get_me()
    
    print(f"✅ Authenticated as: {me.first_name} (@{me.username})")
    print(f"📱 Phone: {me.phone}")
    print(f"🆔 User ID: {me.id}")
    print("=" * 60)
    print("✅ Session saved! You can now run python main.py")
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
