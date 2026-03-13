import discord
from discord.ext import commands
from discord import app_commands
import os
import json
import settings

WELCOME_ENABLED = True  # Set to False to disable welcome messages
WELCOME_CHANNEL_ID = 1344969966843203666  # Replace with your channel ID
GODBOT_ROLE_ID = 1380183599013429388  # Role to grant access

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data.json")

def load_data():
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        with open(DATA_FILE, "w") as f:
            json.dump({"wallets": {}, "xp": {}}, f)
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        with open(DATA_FILE, "w") as f:
            json.dump({"wallets": {}, "xp": {}}, f)
        return {"wallets": {}, "xp": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not WELCOME_ENABLED:
            return
        guild = member.guild
        channel = guild.get_channel(WELCOME_CHANNEL_ID)
        if channel:
            await channel.send(
                f"Welcome to the server, {member.mention}!\n"
                f"Use '/godbotaccess' to access botcommand channel, XP, leaderboards, economy, and shop.\n"
                f"You received free XP and {settings.CURRENCY_NAME}.\n"
                f"Enjoy your stay!"
            )
        # Give 100 XP and 100 currency
        data = load_data()
        user_id = str(member.id)
        data.setdefault("xp", {})
        data.setdefault("wallets", {})
        data["xp"][user_id] = data["xp"].get(user_id, 0) + 100
        data["wallets"][user_id] = data["wallets"].get(user_id, 0) + 100
        save_data(data)

    @app_commands.command(name="godbotaccess", description="Get access to command channel, leaderboards, and shop.")
    async def godbotaccess(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user
        role = guild.get_role(GODBOT_ROLE_ID)
        if not role:
            await interaction.response.send_message("GodBot access role not found. Please contact an admin.", ephemeral=True)
            return
        if role in member.roles:
            await interaction.response.send_message("You already have GodBot access!", ephemeral=True)
            return
        await member.add_roles(role)
        await interaction.response.send_message(
            f"{member.mention}, you have been given access to the command channel, leaderboards, and shop!", ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Welcome(bot))



