import discord
from discord.ext import commands
from discord import app_commands
import random
import os
import json
import asyncio
from datetime import datetime, timedelta
import pytz
import settings

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data.json")
TIMEZONE = pytz.timezone("Europe/Lisbon")  # Western European Time

def load_data():
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        with open(DATA_FILE, "w") as f:
            json.dump({"wallets": {}, "inventory": {}}, f)
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        with open(DATA_FILE, "w") as f:
            json.dump({"wallets": {}, "inventory": {}}, f)
        return {"wallets": {}, "inventory": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

GOLD_MINE_EQUIPMENT = [
    "Bulldozers",
    "Excavators",
    "Dump Trucks",
    "Wash Plant",
    "Trommel",
    "Generators & Pumps",
    "Gold Tables & Sluices"
]

class GoldMine(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mining_members = set()

    async def cog_load(self):
        guild = discord.Object(id=settings.GUILD_ID)
        self.bot.tree.add_command(self.mine, guild=guild)

    @app_commands.command(name="mine", description="Mine for gold! Requires all gold mine equipment.")
    async def mine(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        username = interaction.user.display_name
        data = load_data()
        wallets = data.setdefault("wallets", {})
        inventory = data.setdefault("inventory", {})
        user_inv = inventory.setdefault(user_id, [])

        # Check for required mining equipment (adjust as needed)
        required_items = [
            "Bulldozers",
            "Excavators",
            "Dump Trucks",
            "Wash Plant",
            "Trommel",
            "Generators & Pumps",
            "Gold Tables & Sluices"
        ]
        missing = [item for item in required_items if item not in user_inv]
        if missing:
            await interaction.response.send_message(
                f"You need all Gold Mine equipment to mine:\n" +
                "\n".join(f"- {item}" for item in missing),
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"{username} started mining! Mining will continue the rest of this day. You'll find gold as you mine...",
            ephemeral=False
        )

        findings = []
        total_value = 0

        # Generate all findings for the session
        num_dust = random.randint(10, 15)
        num_flakes = random.randint(3, 5)
        found_nugget = random.random() < 0.5

        # Create a list of all findings
        all_findings = [("Gold Dust", random.randint(1, 49)) for _ in range(num_dust)]
        all_findings += [("Gold Flake", random.randint(50, 500)) for _ in range(num_flakes)]
        if found_nugget:
            all_findings.append(("Gold Nugget", random.randint(500, 5000)))

        random.shuffle(all_findings)  # Shuffle so discoveries are random

        # Calculate seconds until 23:59 WET today
        now = datetime.now(TIMEZONE)
        end_time = now.replace(hour=23, minute=59, second=0, microsecond=0)
        if end_time <= now:
            end_time += timedelta(days=1)
        seconds_left = int((end_time - now).total_seconds())

        # Spread findings over the remaining time today
        interval = max(1, seconds_left // len(all_findings))
        for item_name, value in all_findings:
            await asyncio.sleep(interval)
            findings.append((item_name, value))
            total_value += value
            await interaction.channel.send(
                f"⛏️ {username} found {item_name} worth {value} {settings.CURRENCY_NAME}!"
            )

        # Add total value to user's wallet
        wallets[user_id] = wallets.get(user_id, 0) + total_value
        save_data(data)

        # Summary
        summary = (
            f"{username} found {len(findings)} items.\n"
            f"Total value: {total_value} {settings.CURRENCY_NAME}.\n"
            f"Current balance: {wallets[user_id]} {settings.CURRENCY_NAME}."
        )
        await interaction.channel.send(summary)

async def setup(bot):
    await bot.add_cog(GoldMine(bot))