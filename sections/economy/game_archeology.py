import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
import os
import json
import settings
import time

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data.json")

ARCHAEOLOGY_FINDINGS = [
    ("Ancient Coin", 150, 18),
    ("Dinosaur Bone", 200, 8),
    ("Lost Relic", 250, 5),
    ("Fossilized Leaf", 160, 20),
    ("Golden Scarab", 350, 3),
    ("Clay Tablet", 170, 15),
    ("Jeweled Goblet", 300, 4),
    ("Mysterious Idol", 270, 6),
    ("Old Map Fragment", 180, 12),
    ("Crystal Skull", 220, 7),
    ("Bronze Arrowhead", 155, 16),
    ("Obsidian Knife", 210, 7),
    ("Ancient Dice", 165, 14),
    ("Roman Pendant", 230, 9),
    ("Silver Bracelet", 240, 8),
    ("Stone Figurine", 175, 13),
    ("Viking Brooch", 260, 6),
    ("Medieval Key", 185, 11),
    ("Amber Amulet", 195, 10),
    ("Ceramic Mask", 225, 8),
    ("Copper Ring", 160, 15),
    ("Runestone Fragment", 200, 9),
    ("Ivory Comb", 170, 14),
    ("Glass Bead", 150, 17),
    ("Ancient Earring", 180, 12),
    ("Pharaoh's Scarab", 320, 4),
    ("Jade Talisman", 280, 5),
    ("Silver Coin", 190, 13),
    ("Ornate Button", 175, 14),
    ("Miniature Idol", 210, 7),
    ("Old Compass", 250, 5),
]

ARCHAEOLOGY_FINDING_NAMES = {item[0] for item in ARCHAEOLOGY_FINDINGS}

def load_data():
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        with open(DATA_FILE, "w") as f:
            json.dump({"wallets": {}, "inventory": {}, "xp": {}, "nuggets": {}}, f)
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        with open(DATA_FILE, "w") as f:
            json.dump({"wallets": {}, "inventory": {}, "xp": {}, "nuggets": {}}, f)
        return {"wallets": {}, "inventory": {}, "xp": {}, "nuggets": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class Archeology(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.digging_members = set()

    @app_commands.command(name="dig", description="Dig for ancient items! 1 hour dig, random finds.")
    async def dig(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        username = interaction.user.display_name
        if user_id in self.digging_members:
            await interaction.response.send_message("You are already digging! Please wait for your current dig to finish.", ephemeral=True)
            return
        data = load_data()
        inventory = data.setdefault("inventory", {})
        user_inv = inventory.setdefault(user_id, [])

        required_items = [
            "Indiana Jones's Map",
            "Indiana Jones's Whip",
            "Indiana Jones's Shovel",
            "Indiana Jones's Brush"
        ]
        missing = [item for item in required_items if item not in user_inv]
        if missing:
            await interaction.response.send_message(
                f"You need all Archeology equipment to dig:\n" +
                "\n".join(f"- {item}" for item in missing),
                ephemeral=True
            )
            return

        self.digging_members.add(user_id)
        findings = []
        nugget_count = 0
        total_value = 0
        channel = interaction.channel

        try:
            wallets = data.setdefault("wallets", {})
            nuggets = data.setdefault("nuggets", {})

            await interaction.response.send_message(f"{username} started digging! This will take 1 hour. You'll find items as you dig...", ephemeral=False)
            await interaction.followup.send("Digging started...")

            num_findings = random.randint(10, 15)
            delays = sorted(random.sample(range(1, 3600), num_findings))  # seconds in 1 hour

            last_delay = 0
            for i, delay in enumerate(delays):
                await asyncio.sleep(delay - last_delay)
                last_delay = delay
                item = random.choice(ARCHAEOLOGY_FINDINGS)
                findings.append(item)
                total_value += item[1]

                # Remove all occurrences of the found item from all inventories (string or tuple)
                for member_id, inv in inventory.items():
                    inventory[member_id] = [
                        inv_item for inv_item in inv
                        if not (
                            (isinstance(inv_item, str) and inv_item == item[0])
                            or (isinstance(inv_item, tuple) and inv_item[0] == item[0])
                        )
                    ]

                try:
                    await interaction.followup.send(f"⛏️ {username} found **{item[0]}** worth {item[1]} {settings.CURRENCY_NAME}!", ephemeral=False)
                except Exception:
                    try:
                        await channel.send(f"⛏️ {username} found **{item[0]}** worth {item[1]} {settings.CURRENCY_NAME}!")
                    except Exception:
                        pass

                if random.random() < 0.10:
                    nugget_count += 1
                    nuggets[user_id] = nuggets.get(user_id, 0) + 1
                    try:
                        await interaction.followup.send(f"✨ {username} found a **golden nugget**!", ephemeral=False)
                    except Exception:
                        try:
                            await channel.send(f"✨ {username} found a **golden nugget**!")
                        except Exception:
                            pass

                save_data(data)

            # Add total value to user's wallet (only add, never subtract)
            if total_value > 0:
                wallets[user_id] = wallets.get(user_id, 0) + total_value
                save_data(data)

        except Exception as e:
            try:
                await interaction.followup.send(f"Dig failed due to an error: {e}", ephemeral=True)
            except Exception:
                try:
                    await channel.send(f"Dig failed due to an error: {e}")
                except Exception:
                    pass
        finally:
            # Always reload data to get the latest wallet and nugget value
            data = load_data()
            wallets = data.setdefault("wallets", {})
            nuggets = data.setdefault("nuggets", {})
            current_balance = wallets.get(user_id, 0)
            current_nuggets = nuggets.get(user_id, 0)
            summary = (
                f"{username} found {len(findings)} items.\n"
                f"Total value: {total_value} {settings.CURRENCY_NAME}.\n"
                f"Golden nuggets found: {nugget_count} (now {current_nuggets} in inventory).\n"
                f"Current balance: {current_balance} {settings.CURRENCY_NAME}."
            )
            try:
                await interaction.followup.send(summary, ephemeral=False)
            except Exception:
                try:
                    await channel.send(summary)
                except Exception:
                    pass
            self.digging_members.discard(user_id)

    async def cog_load(self):
        guild = discord.Object(id=settings.GUILD_ID)
        self.bot.tree.add_command(self.dig, guild=guild)

async def setup(bot):
    await bot.add_cog(Archeology(bot))