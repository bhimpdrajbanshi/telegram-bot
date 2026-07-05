import asyncio
import logging
import os
import sys
import time
from collections import defaultdict
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, BotCommand
from aiogram.exceptions import TelegramRetryAfter

import ollama

# 1. Setup Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    logging.error("BOT_TOKEN is missing!")
    sys.exit(1)

dp = Dispatcher()
OLLAMA_MODEL = "Qwen2.5:3b-Instruct" 

# Memory and Custom Personas
MAX_MEMORY = 10
conversation_memory = defaultdict(list)

DEFAULT_SYSTEM_PROMPT = "You are a helpful, concise Telegram AI assistant."

PERSONAS = {
    "assistant": "You are a helpful, concise Telegram AI assistant.",
    "coder": "You are an elite senior software engineer. Code clean, elegant solutions and explain them shortly.",
    "teacher": "You are a patient teacher. Explain complex topics using simple analogies for beginners.",
    "pirate": "You are a funny pirate captain. Answer everything using aggressive pirate slang and pirate humor!"
}

# Helper to get or initialize chat memory
def get_memory(chat_id: int):
    if chat_id not in conversation_memory or not conversation_memory[chat_id]:
        conversation_memory[chat_id] = [{"role": "system", "content": DEFAULT_SYSTEM_PROMPT}]
    return conversation_memory[chat_id]

# Command: Start / Reset
@dp.message(Command("start", "reset"))
async def command_reset_handler(message: Message) -> None:
    chat_id = message.chat.id
    conversation_memory[chat_id] = [{"role": "system", "content": DEFAULT_SYSTEM_PROMPT}]
    await message.answer("🔄 Memory cleared! I am back to my default helpful assistant mode.")

# Commands: Persona Switchers
@dp.message(Command("coder", "teacher", "pirate", "assistant"))
async def command_persona_handler(message: Message) -> None:
    chat_id = message.chat.id
    # Extract command text (e.g., 'coder' from '/coder')
    command_name = message.text.strip("/").split()[0]
    
    selected_prompt = PERSONAS.get(command_name, DEFAULT_SYSTEM_PROMPT)
    conversation_memory[chat_id] = [{"role": "system", "content": selected_prompt}]
    
    await message.answer(f"🎭 Persona switched to **{command_name.upper()}**! Memory has been reset.")

# 3. Main Handler: Token Streaming Architecture
@dp.message()
async def ai_streaming_handler(message: Message) -> None:
    if not message.text:
        return

    chat_id = message.chat.id
    user_text = message.text

    await message.bot.send_chat_action(chat_id=chat_id, action="typing")

    # Fetch context and append user prompt
    history = get_memory(chat_id)
    history.append({"role": "user", "content": user_text})

    # Send placeholder message to user
    sent_message = await message.answer("⏳ *Thinking...*", parse_mode="Markdown")
    
    full_response = ""
    last_ui_update_time = time.time()
    update_interval = 0.5  # Only update Telegram UI every 0.5 seconds to dodge rate-limits

    try:
        # Use the AsyncClient for non-blocking stream iteration
        async_client = ollama.AsyncClient()
        stream = await async_client.chat(
            model=OLLAMA_MODEL,
            messages=history,
            stream=True
        )

        async for chunk in stream:
            token = chunk['message']['content']
            full_response += token
            
            current_time = time.time()
            # If interval passed, safely edit the message on the fly
            if current_time - last_ui_update_time > update_interval:
                try:
                    await sent_message.edit_text(full_response + " ▌")
                    last_ui_update_time = current_time
                except TelegramRetryAfter as e:
                    # If we hit flood limits, wait it out dynamically
                    await asyncio.sleep(e.retry_after)
                except Exception:
                    pass # Ignore trivial telemetry update skips

        # Stream complete: drop the typing cursor symbol "▌"
        await sent_message.edit_text(full_response)
        
        # Save complete generation back into memory array
        history.append({"role": "assistant", "content": full_response})
        if len(history) > MAX_MEMORY:
            # Maintain system instructions while cleaning ancient chat logs
            conversation_memory[chat_id] = [history[0]] + history[-MAX_MEMORY:]

    except Exception as e:
        logging.error(f"Streaming failure: {e}")
        await sent_message.edit_text("Sorry, my local AI brain tripped over a connection error.")

# Register commands into Telegram menu button UI automatically
async def main() -> None:
    bot = Bot(token=TOKEN)
    
    # Inject command blueprints into the user's interface chat menu button
    await bot.set_my_commands([
        BotCommand(command="start", description="Start bot / Reset Memory"),
        BotCommand(command="assistant", description="Set to default AI Assistant"),
        BotCommand(command="coder", description="Set to Senior Software Engineer Persona"),
        BotCommand(command="teacher", description="Set to Friendly Academic Tutor Persona"),
        BotCommand(command="pirate", description="Set to Captain Pirate Persona")
    ])
    
    logging.info(f"⚡ Streaming Engine running on model: {OLLAMA_MODEL}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.exception("Fatal crash:")
