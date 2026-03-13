import discord
from discord.ext import commands
from discord import app_commands
import settings
import json
import os

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data.json")
XP_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "xp.json")  # If you store XP separately

def load_data():
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        with open(DATA_FILE, "w") as f:
            json.dump({"bank": 0, "wallets": {}}, f)
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        with open(DATA_FILE, "w") as f:
            json.dump({"bank": 0, "wallets": {}}, f)
        return {"bank": 0, "wallets": {}}

def load_xp():
    # Load XP from data.json
    data_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data.json")
    if not os.path.exists(data_file) or os.path.getsize(data_file) == 0:
        return {}
    try:
        with open(data_file, "r") as f:
            data = json.load(f)
            return data.get("xp", {})
    except json.JSONDecodeError:
        return {}

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="profile", description="Show your or another member's profile.")
    async def profile(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        data = load_data()
        xp_data = load_xp()

        # XP and Leaderboard
        user_xp = xp_data.get(str(member.id), 0)
        xp_leaderboard = sorted(xp_data.items(), key=lambda x: x[1], reverse=True)
        xp_position = next((i+1 for i, (uid, _) in enumerate(xp_leaderboard) if uid == str(member.id)), None)

        # Connected Rank: Find the highest role the user qualifies for by XP
        connected_role = None
        for threshold, role_id in sorted(settings.CONNECTED_RANKS, reverse=True):
            if user_xp >= threshold:
                connected_role = discord.utils.get(member.guild.roles, id=role_id)
                break
        connected_rank = connected_role.name if connected_role else "Unranked"

        # Wallet and Leaderboard
        wallets = data.get("wallets", {})
        wallet_balance = wallets.get(str(member.id), 0)
        wallet_leaderboard = sorted(wallets.items(), key=lambda x: x[1], reverse=True)
        wallet_position = next((i+1 for i, (uid, _) in enumerate(wallet_leaderboard) if uid == str(member.id)), None)

        # Highest Role
        highest_role = member.top_role.name if len(member.roles) > 1 else "None"

        # Nuggets
        nuggets = data.get("nuggets", {})
        nugget_balance = nuggets.get(str(member.id), 0)

        # Inventory
        inventory = data.get("inventory", {})
        user_items = inventory.get(str(member.id), [])
        if user_items:
            items_str = "\n".join(f"- {item}" for item in user_items)
        else:
            items_str = "No items owned."

        embed = discord.Embed(
            title=f"{member.display_name}'s Profile",
            color=0x00ffee  # Set default embed color to 00ffee
        )
        # XP block (grouped, each on its own line)
        xp_block = (
            f"XP: {user_xp}\n"
            f"XP Leaderboard Position: {xp_position or 'N/A'}\n"
            f"Connected Rank: {connected_rank}"
        )
        embed.add_field(name="XP Stats", value=xp_block, inline=False)

        # Wallet block (grouped, each on its own line)
        wallet_block = (
            f"Wallet Balance: {wallet_balance} {settings.CURRENCY_NAME}\n"
            f"Gold Nuggets: {nugget_balance}\n"
            f"Wallet Leaderboard Position: {wallet_position or 'N/A'}"
        )
        embed.add_field(name="Wallet Stats", value=wallet_block, inline=False)

        # Highest Role
        embed.add_field(name="Highest Role", value=highest_role, inline=False)

        # Items
        embed.add_field(name="Owned Items", value=items_str, inline=False)

        await interaction.response.send_message(embed=embed)

    async def cog_load(self):
        guild = discord.Object(id=settings.GUILD_ID)
        self.bot.tree.add_command(self.profile, guild=guild)

async def setup(bot):
    await bot.add_cog(Profile(bot))