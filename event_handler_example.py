"""
Example: How to integrate the Top Early Trending filter into your event handler

Add this to your .env file:
SKIP_TRENDING_UPDATES=true         # Set to 'false' to forward all messages including rankings
"""

import os
from filters import should_forward_message


@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def forward_handler(event):
    try:
        message = event.message
        original_text = message.text

        # NEW: Check if message should be skipped
        # Respects the SKIP_TRENDING_UPDATES environment variable
        if original_text and not should_forward_message(original_text):
            print(f"[SKIP] Ignoring Top Early Trending update (ID: {message.id})")
            return  # Don't forward this message

        # ... rest of your existing forwarding logic ...
        print(f"[FORWARD] Processing message (ID: {message.id})")

        # Your forwarding code here
        # await forward_message(message)

    except Exception as e:
        print(f"[ERROR] {e}")


# Alternative: Override environment variable programmatically
@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def forward_handler_with_override(event):
    try:
        message = event.message
        original_text = message.text

        # Force skip trending updates regardless of env var
        if original_text and not should_forward_message(original_text, skip_trending=True):
            print(f"[SKIP] Ignoring Top Early Trending update (ID: {message.id})")
            return

        # Force forward all messages including trending
        if original_text and not should_forward_message(original_text, skip_trending=False):
            print(f"[FORCE] Forwarding all messages (ID: {message.id})")
            # Will forward everything including trending updates

        # Your forwarding code here

    except Exception as e:
        print(f"[ERROR] {e}")
