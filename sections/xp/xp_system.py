import discord
from discord.ext import commands, tasks
from discord import app_commands
import settings
import json
import os
from datetime import datetime, timedelta, time
import pytz
import asyncio

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data.json")
EVENT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "eventlive.json")

XP_ROLE_THRESHOLDS = [
    (10, 1375428707765981194),
    (10000, 1405074856243888139),
]
REMOVE_PREVIOUS_XP_ROLE = False  # Set to False to keep previous roles

TIMEZONE = pytz.timezone("Europe/Lisbon")

def load_data():
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        with open(DATA_FILE, "w") as f:
            json.dump({"xp": {}, "wallets": {}, "warnings": {}}, f)
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        with open(DATA_FILE, "w") as f:
            json.dump({"xp": {}, "wallets": {}, "warnings": {}}, f)
        return {"xp": {}, "wallets": {}, "warnings": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_event():
    if not os.path.exists(EVENT_FILE) or os.path.getsize(EVENT_FILE) == 0:
        with open(EVENT_FILE, "w") as f:
            json.dump({"eventlive": False}, f)
    try:
        with open(EVENT_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        with open(EVENT_FILE, "w") as f:
            json.dump({"eventlive": False}, f)
        return {"eventlive": False}

def save_event(data):
    with open(EVENT_FILE, "w") as f:
        json.dump(data, f, indent=4)

class XPSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_times = {}

    async def cog_load(self):
        guild = discord.Object(id=settings.GUILD_ID)
        self.bot.tree.add_command(self.eventlive, guild=guild)
        self.bot.tree.add_command(self.xpset, guild=guild)
        self.voice_xp_task.start()
        self.xp_role_check_task.start()

    def get_xp_multiplier(self):
        event = load_event()
        multiplier = settings.XP_MULTIPLIER
        if event.get("eventlive", False):
            multiplier *= settings.XP_EVENT_MULTIPLIER
        return multiplier

    def get_highest_xp_role(self, xp):
        """Return the highest role_id for the given xp."""
        role_id = None
        for threshold, rid in sorted(XP_ROLE_THRESHOLDS):
            if xp >= threshold:
                role_id = rid
        return role_id

    async def update_xp_roles(self, member, new_xp):
        guild = member.guild
        highest_role_id = self.get_highest_xp_role(new_xp)
        if not highest_role_id:
            return
        role = guild.get_role(highest_role_id)
        if not role:
            return

        # Remove previous XP roles if needed
        if REMOVE_PREVIOUS_XP_ROLE:
            for _, rid in XP_ROLE_THRESHOLDS:
                prev_role = guild.get_role(rid)
                if prev_role and prev_role in member.roles and prev_role != role:
                    await member.remove_roles(prev_role)

        # Add the new role if not already present
        if role not in member.roles:
            await member.add_roles(role)

    def add_xp(self, user_id, base_xp, activity_name="activity"):
        data = load_data()
        xp_data = data.setdefault("xp", {})
        event = load_event()
        multiplier = settings.XP_MULTIPLIER
        event_multiplier = settings.XP_EVENT_MULTIPLIER if event.get("eventlive", False) else 1.0
        total_xp = int(base_xp * multiplier * event_multiplier)
        xp_data[str(user_id)] = xp_data.get(str(user_id), 0) + total_xp
        data["xp"] = xp_data
        save_data(data)

        # XP role check
        member = self.bot.get_guild(settings.GUILD_ID).get_member(int(user_id))
        if member:
            self.bot.loop.create_task(self.update_xp_roles(member, xp_data[str(user_id)]))

        # Log calculation to BOT_LOG_CHANNEL_ID
        channel = self.bot.get_channel(settings.BOT_LOG_CHANNEL_ID)
        if channel:
            user = member.display_name if member else str(user_id)
            msg = (
                f"{user}  Total xp received ({total_xp}) = xp received for {activity_name} ({base_xp}) "
                f"* XP_MULTIPLIER ({multiplier})"
            )
            if event.get("eventlive", False):
                msg += f" * XP_EVENT_MULTIPLIER ({settings.XP_EVENT_MULTIPLIER})"
            asyncio.create_task(channel.send(msg))

        return xp_data[str(user_id)]

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        self.add_xp(message.author.id, settings.XP_for_message, activity_name="message")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return
        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if member is None or member.bot:
            return

        # Only one XP per message per user for emoji reaction
        key = f"{payload.message_id}:{payload.user_id}:emoji"
        if not hasattr(self, "reaction_cache"):
            self.reaction_cache = set()
        if key in self.reaction_cache:
            return
        self.reaction_cache.add(key)
        self.add_xp(payload.user_id, settings.XP_for_emoji_reaction, activity_name="emoji reaction")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return
        now = datetime.utcnow()
        if after.channel and not before.channel:
            # Joined a voice channel
            self.voice_times[member.id] = (after.channel.id, now)
        elif before.channel and not after.channel:
            # Left a voice channel
            if member.id in self.voice_times:
                join_time = self.voice_times[member.id][1]
                minutes = int((now - join_time).total_seconds() // 60)
                xp_earned = (minutes // 10) * settings.XP_for_voice
                if xp_earned > 0:
                    self.add_xp(member.id, xp_earned, activity_name="voice")
                del self.voice_times[member.id]

    @tasks.loop(minutes=10)
    async def voice_xp_task(self):
        now = datetime.utcnow()
        for user_id, (channel_id, join_time) in list(self.voice_times.items()):
            minutes = int((now - join_time).total_seconds() // 60)
            xp_earned = (minutes // 10) * settings.XP_for_voice
            if xp_earned > 0:
                self.add_xp(user_id, xp_earned, activity_name="voice")
                self.voice_times[user_id] = (channel_id, now)

    @tasks.loop(time=time(hour=12, minute=0, tzinfo=TIMEZONE))
    async def xp_role_check_task(self):
        await self.bot.wait_until_ready()
        data = load_data()
        xp_data = data.get("xp", {})
        guild = self.bot.get_guild(settings.GUILD_ID)
        if not guild:
            return
        for user_id, xp in xp_data.items():
            member = guild.get_member(int(user_id))
            if member:
                await self.update_xp_roles(member, xp)

    @app_commands.command(name="eventlive", description="Set event live status for XP multiplier.")
    @app_commands.describe(status="True to enable event XP, False to disable")
    async def eventlive(self, interaction: discord.Interaction, status: bool):
        # Only owner or moderator can use
        is_owner = interaction.user.id == settings.OWNER_ID
        is_mod = False
        moderator_role_id = getattr(settings, "Moderator_role_ID", None)
        if moderator_role_id:
            is_mod = any(role.id == moderator_role_id for role in interaction.user.roles)
        if not (is_owner or is_mod):
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return

        event = load_event()
        event["eventlive"] = status
        save_event(event)
        await interaction.response.send_message(f"Event live set to **{status}**.", ephemeral=False)

    async def member_autocomplete(self, interaction: discord.Interaction, current: str):
        # Suggest "everybody" and up to 20 matching member names
        members = [
            app_commands.Choice(name="everybody", value="everybody")
        ]
        for member in interaction.guild.members:
            if member.bot:
                continue
            display = f"{member.display_name} ({member.name})"
            if current.lower() in display.lower():
                members.append(app_commands.Choice(name=display, value=str(member.id)))
            if len(members) >= 20:
                break
        return members

    @app_commands.command(name="xpset", description="Set XP for a member or all members. Only owner or moderators can use this.")
    @app_commands.describe(
        amount="The XP amount to set",
        member="The member to set XP for, or type 'everybody' to set for all members"
    )
    @app_commands.autocomplete(member=member_autocomplete)
    async def xpset(self, interaction: discord.Interaction, amount: int, member: str):
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
        xp_data = data.setdefault("xp", {})

        if member.lower() == "everybody":
            count = 0
            for m in interaction.guild.members:
                if not m.bot:
                    xp_data[str(m.id)] = amount
                    count += 1
            msg = f"Set XP for all members to {amount} ({count} members updated)."
        else:
            # Try to find the member by name or mention
            target_member = discord.utils.find(
                lambda m: m.name == member or m.display_name == member or str(m.id) == member.replace('<@', '').replace('>', ''),
                interaction.guild.members
            )
            if not target_member or target_member.bot:
                await interaction.response.send_message("Member not found or is a bot.", ephemeral=True)
                return
            xp_data[str(target_member.id)] = amount
            msg = f"Set XP for {target_member.mention} to {amount}."

        data["xp"] = xp_data
        save_data(data)
        await interaction.response.send_message(msg, ephemeral=False)

async def setup(bot):
    await bot.add_cog(XPSystem(bot))