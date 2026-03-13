import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os
from datetime import datetime
import pytz
import settings
import asyncio
logger = settings.logger

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data.json")
TIMEZONE = pytz.timezone("Europe/Lisbon")  # Western European Time

def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({"bank": 0, "wallets": {}}, f)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_daily = None
        self.last_tax = None
        # DO NOT start tasks here!

    def cog_unload(self):
        self.daily_reward.cancel()
        self.tax_collection.cancel()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        data = load_data()
        user_id = str(message.author.id)
        wallets = data.setdefault("wallets", {})
        wallets[user_id] = wallets.get(user_id, 0) + 1
        save_data(data)
        logger.info(f"Added 1 {settings.CURRENCY_NAME} to user {user_id} for sending a message.")

    @tasks.loop(minutes=1)
    async def daily_reward(self):
        now = datetime.now(TIMEZONE)
        if now.hour == 12 and now.minute == 0:
            if self.last_daily == now.date():
                return
            data = load_data()
            for member in self.bot.get_all_members():
                if member.bot:
                    continue
                user_id = str(member.id)
                wallets = data.setdefault("wallets", {})
                wallets[user_id] = wallets.get(user_id, 0) + 10
                logger.info(f"Gave daily reward to user {user_id}.")
            save_data(data)
            self.last_daily = now.date()
            logger.info("Daily reward distributed.")

    @tasks.loop(minutes=1)
    async def tax_collection(self):
        now = datetime.now(TIMEZONE)
        if now.weekday() == 6 and now.hour == 12 and now.minute == 0:
            if self.last_tax == now.date():
                return
            data = load_data()
            bank = data.setdefault("bank", 0)
            wallets = data.setdefault("wallets", {})
            for user_id, balance in wallets.items():
                tax = 0
                for threshold, rate in settings.TAX_BRACKETS:
                    if balance >= threshold:
                        tax = int(balance * rate)
                wallets[user_id] -= tax
                data["bank"] += tax
                logger.info(f"Collected {tax} {settings.CURRENCY_NAME} in taxes from user {user_id}.")
            save_data(data)
            self.last_tax = now.date()
            logger.info("Taxes collected.")

    @app_commands.command(name="bank", description="Check the bank's balance.")
    async def bank(self, interaction: discord.Interaction):
        data = load_data()
        bank = data.get("bank", 0)
        await interaction.response.send_message(f"The bank has {bank} {settings.CURRENCY_NAME}.")

    @app_commands.command(name="moneyset", description="Set wallet balance for a member or all members. Only owner or moderators can use this.")
    @app_commands.describe(
        amount="The wallet amount to set",
        member="The member to set money for (leave empty for everybody)"
    )
    async def moneyset(self, interaction: discord.Interaction, amount: int, member: discord.Member = None):
        # Only allow owner or moderators
        is_owner = interaction.user.id == settings.OWNER_ID
        is_mod = False
        moderator_role_id = getattr(settings, "Moderator_role_ID", None)
        if moderator_role_id:
            is_mod = any(role.id == moderator_role_id for role in interaction.user.roles)
        if not (is_owner or is_mod):
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return

        data = load_data()
        wallets = data.setdefault("wallets", {})

        if member is None:
            count = 0
            for m in interaction.guild.members:
                if not m.bot:
                    wallets[str(m.id)] = amount
                    count += 1
            msg = f"Set wallet balance for all members to {amount} {settings.CURRENCY_NAME} ({count} members updated)."
        else:
            if member.bot:
                await interaction.response.send_message("Member is a bot.", ephemeral=True)
                return
            wallets[str(member.id)] = amount
            msg = f"Set wallet balance for {member.mention} to {amount} {settings.CURRENCY_NAME}."

        data["wallets"] = wallets
        save_data(data)
        await interaction.response.send_message(msg, ephemeral=False)

    async def cog_load(self):
        guild = discord.Object(id=settings.GUILD_ID)
        self.bot.tree.add_command(self.bank, guild=guild)
        self.bot.tree.add_command(self.moneyset, guild=guild)
        self.daily_reward.start()
        self.tax_collection.start()