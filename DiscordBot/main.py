import discord
from discord.ext import commands
import os
import asyncio

# Setup required intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Define a basic logging function for the Welcome Bot.
# You can expand this to send logs to a specific channel or external system.
async def send_log(guild: discord.Guild, message: str):
    # For example, simply print the log. Replace or extend with your own implementation.
    print(f"[{guild.name}] {message}")

# Attach the logging function to the bot instance.
bot.send_log = send_log

# Function to load all extensions from a given folder.
async def load_extensions(bot: commands.Bot):
    for folder in ["cogs", "events"]:
        if not os.path.isdir(folder):
            continue
        for filename in os.listdir(folder):
            if filename.endswith(".py") and filename != "__init__.py":
                ext = f"{folder}.{filename[:-3]}"
                try:
                    await bot.load_extension(ext)
                    print(f"Loaded extension: {ext}")
                except Exception as e:
                    print(f"Failed to load extension {ext}: {e}")

@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}.")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} global command(s).")
    except Exception as e:
        print(f"Error syncing commands: {e}")

async def main():
    async with bot:
        await load_extensions(bot)
        # Replace "YOUR_TOKEN" with your bot token
        await bot.start("MTM0NDMzMzg0MzA2MjA2MzE0NQ.G3NHTU.xb9ka88ZJZVNbixSfskCCWBCGA7SQSYxFKW-2Y")

if __name__ == "__main__":
    asyncio.run(main())
