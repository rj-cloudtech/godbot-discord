import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv  # <-- Add this import
import settings

load_dotenv()  # <-- Load variables from .env

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    guild = discord.Object(id=settings.GUILD_ID)
    await bot.tree.sync(guild=guild)
    print(f"Synced commands to guild {settings.GUILD_ID}")
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

async def load_cogs():
    base_dir = os.path.join(os.path.dirname(__file__), "sections")
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                rel_path = os.path.relpath(os.path.join(root, file), os.path.dirname(__file__))
                module = rel_path.replace(os.sep, ".")[:-3]  # remove .py
                try:
                    await bot.load_extension(module)
                    print(f"Loaded cog: {module}")
                except Exception as e:
                    print(f"Failed to load cog {module}: {e}")

async def main():
    await load_cogs()
    await bot.start(os.getenv("BOT_TOKEN"))  # Token loaded from .env

if __name__ == "__main__":
    asyncio.run(main())