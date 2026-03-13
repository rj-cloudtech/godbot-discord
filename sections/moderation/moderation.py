import discord
from discord.ext import commands
from discord import app_commands
import settings
import json
import os
from datetime import datetime, timedelta

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data.json")

def load_data():
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        with open(DATA_FILE, "w") as f:
            json.dump({"warnings": {}}, f)
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        with open(DATA_FILE, "w") as f:
            json.dump({"warnings": {}}, f)
        return {"warnings": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def cleanup_warnings(warnings):
    now = datetime.utcnow()
    cleaned = {}
    for user_id, warns in warnings.items():
        active_warns = [
            w for w in warns
            if (now - datetime.fromisoformat(w["timestamp"])) < timedelta(days=30)
        ]
        if active_warns:
            cleaned[user_id] = active_warns
    return cleaned

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def has_move_permission(self, member: discord.Member):
        move_role_id = getattr(settings, "MOVE_ROLE_ID", None)
        if move_role_id:
            return any(role.id == move_role_id for role in member.roles)
        return member.guild_permissions.move_members

    @app_commands.command(name="move", description="Move all members from one voice channel to another (requires move permission).")
    @app_commands.describe(
        from_channel_name="The name of the voice channel to move members from",
        to_channel_name="The name of the voice channel to move members to"
    )
    async def move(self, interaction: discord.Interaction, from_channel_name: str, to_channel_name: str):
        if not self.has_move_permission(interaction.user):
            await interaction.response.send_message("You do not have permission to move members.", ephemeral=True)
            return

        voice_channels = [c for c in interaction.guild.voice_channels]
        channel_names = [c.name for c in voice_channels]

        from_channel = discord.utils.get(voice_channels, name=from_channel_name)
        to_channel = discord.utils.get(voice_channels, name=to_channel_name)

        if not from_channel or not to_channel:
            suggestion = "\n".join(channel_names)
            await interaction.response.send_message(
                f"Channel not found. Available voice channels:\n{suggestion}", ephemeral=True
            )
            return

        moved = 0
        for member in from_channel.members:
            try:
                await member.move_to(to_channel)
                moved += 1
            except Exception:
                pass

        await interaction.response.send_message(
            f"Moved {moved} member(s) from **{from_channel.name}** to **{to_channel.name}**.", ephemeral=True
        )

    @app_commands.command(name="warn", description="Warn a member. Only moderators can use this. Warnings expire after 1 month.")
    @app_commands.describe(
        member="The member to warn",
        reason="Reason for the warning (optional)"
    )
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        # Only allow owner or moderators
        is_owner = interaction.user.id == settings.BOT_OWNER_ID
        is_mod = False
        moderator_role_id = getattr(settings, "Moderator_role_ID", None)
        if moderator_role_id:
            is_mod = any(role.id == moderator_role_id for role in interaction.user.roles)
        if not (is_owner or is_mod):
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return

        if member.bot:
            await interaction.response.send_message("You cannot warn bots.", ephemeral=True)
            return

        data = load_data()
        warnings = data.get("warnings", {})
        warnings = cleanup_warnings(warnings)
        user_id = str(member.id)
        warn_entry = {
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        }
        warns = warnings.get(user_id, [])
        warns.append(warn_entry)
        warnings[user_id] = warns
        data["warnings"] = warnings
        save_data(data)

        await interaction.response.send_message(
            f"{member.mention} has received a warning.\n"
            f"Reason: **{reason}**\n"
            f"Total active warnings: **{len(warns)}**.",
            ephemeral=False
        )

    @app_commands.command(name="fine", description="Fine a member. Only moderators can use this.")
    @app_commands.describe(
        member="The member to fine",
        amount=f"Amount of {settings.CURRENCY_NAME} to fine",
        reason="Reason for the fine (optional)"
    )
    async def fine(self, interaction: discord.Interaction, member: discord.Member, amount: int, reason: str = "No reason provided"):
        # Only allow owner or moderators
        is_owner = interaction.user.id == settings.BOT_OWNER_ID
        is_mod = False
        moderator_role_id = getattr(settings, "Moderator_role_ID", None)
        if moderator_role_id:
            is_mod = any(role.id == moderator_role_id for role in interaction.user.roles)
        if not (is_owner or is_mod):
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return

        if member.bot:
            await interaction.response.send_message("You cannot fine bots.", ephemeral=True)
            return

        if amount <= 0:
            await interaction.response.send_message("Amount must be greater than 0.", ephemeral=True)
            return

        # Load wallet data
        data = load_data()
        wallets = data.setdefault("wallets", {})
        user_id = str(member.id)
        balance = wallets.get(user_id, 0)

        if balance < amount:
            await interaction.response.send_message(
                f"{member.mention} does not have enough {settings.CURRENCY_NAME} to be fined that amount.", ephemeral=True
            )
            return

        wallets[user_id] -= amount
        data["wallets"] = wallets
        save_data(data)

        await interaction.response.send_message(
            f"{member.mention} has been fined **{amount} {settings.CURRENCY_NAME}**.\n"
            f"Reason: **{reason}**\n"
            f"New wallet balance: **{wallets[user_id]} {settings.CURRENCY_NAME}**.",
            ephemeral=False
        )

    @app_commands.command(name="xpforrole", description="Give all members with a role a set amount of XP.")
    @app_commands.describe(
        role="The role to give XP to",
        amount="The amount of XP to give"
    )
    async def xpforrole(self, interaction: discord.Interaction, role: discord.Role, amount: int):
        if amount <= 0:
            await interaction.response.send_message("Amount must be greater than 0.", ephemeral=True)
            return

        # Load XP data
        data = load_data()
        xp_data = data.setdefault("xp", {})
        count = 0

        for member in role.members:
            if member.bot:
                continue
            user_id = str(member.id)
            xp_data[user_id] = xp_data.get(user_id, 0) + amount
            count += 1

        data["xp"] = xp_data
        save_data(data)

        await interaction.response.send_message(
            f"Gave **{amount} XP** to **{count}** member(s) with the role {role.mention}.",
            ephemeral=False
        )

    async def cog_load(self):
        guild = discord.Object(id=settings.GUILD_ID)
        self.bot.tree.add_command(self.move, guild=guild)
        self.bot.tree.add_command(self.warn, guild=guild)
        self.bot.tree.add_command(self.fine, guild=guild)
        self.bot.tree.add_command(self.xpforrole, guild=guild)

async def setup(bot):
    await bot.add_cog(Moderation(bot))