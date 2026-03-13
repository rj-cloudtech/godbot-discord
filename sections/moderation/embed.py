import discord
from discord.ext import commands, tasks
from discord import app_commands
import settings
import json
import os
from datetime import datetime
import pytz

EMBED_SCHEDULE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "embed_schedules.json")
TIMEZONE = pytz.timezone("Europe/Lisbon")  # Western European Time

def load_schedules():
    if not os.path.exists(EMBED_SCHEDULE_FILE) or os.path.getsize(EMBED_SCHEDULE_FILE) == 0:
        with open(EMBED_SCHEDULE_FILE, "w") as f:
            json.dump([], f)
    try:
        with open(EMBED_SCHEDULE_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        with open(EMBED_SCHEDULE_FILE, "w") as f:
            json.dump([], f)
        return []

def save_schedules(schedules):
    with open(EMBED_SCHEDULE_FILE, "w") as f:
        json.dump(schedules, f, indent=4)

class EmbedManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_scheduled_embeds.start()

    def cog_unload(self):
        self.check_scheduled_embeds.cancel()

    @app_commands.command(name="embed", description="Owner only: Create an embed from a message and post it.")
    @app_commands.describe(
        title="Embed title (optional)",
        source_channel="Channel to get the source message from",
        message_id="ID of the source message",
        target_channel="Channel to post the embed in",
        when="When to post (now or yyyy-mm-dd hh:mm in WET)",
        color="Embed color (hex, optional, default 00ffee)"
    )
    async def embed(
        self,
        interaction: discord.Interaction,
        title: str = None,
        source_channel: discord.TextChannel = None,
        message_id: str = None,
        target_channel: discord.TextChannel = None,
        when: str = "now",
        color: str = "00ffee"
    ):
        if interaction.user.id != settings.BOT_OWNER_ID:
            await interaction.response.send_message("Only the owner can use this command.", ephemeral=True)
            return

        # Fetch the source message
        try:
            msg = await source_channel.fetch_message(int(message_id))
        except Exception as e:
            await interaction.response.send_message(f"Could not fetch message: {e}", ephemeral=True)
            return

        embed_color = int(color, 16) if color else 0x00ffee
        embed = discord.Embed(
            title=title if title else None,
            description=msg.content,
            color=embed_color
        )
        if msg.attachments:
            embed.set_image(url=msg.attachments[0].url)

        # When to post
        if when.lower() == "now":
            await target_channel.send(embed=embed)
            await interaction.response.send_message("Embed posted.", ephemeral=True)
        else:
            # Parse timestamp
            try:
                dt = datetime.strptime(when, "%Y-%m-%d %H:%M")
                dt = TIMEZONE.localize(dt)
            except Exception:
                await interaction.response.send_message("Invalid timestamp format. Use yyyy-mm-dd hh:mm", ephemeral=True)
                return
            schedules = load_schedules()
            schedules.append({
                "title": title,
                "description": msg.content,
                "image": msg.attachments[0].url if msg.attachments else None,
                "color": color,
                "target_channel_id": target_channel.id,
                "when": dt.isoformat(),
                "author_id": interaction.user.id
            })
            save_schedules(schedules)
            await interaction.response.send_message("Embed scheduled.", ephemeral=True)

    @app_commands.command(name="embededit", description="Owner only: Edit a scheduled or posted embed.")
    @app_commands.describe(
        newtitle="New embed title (optional)",
        source_channel="Channel to get the source message from",
        message_id="ID of the source message",
        target_channel="Channel to post the embed in",
        target_message_id="ID of the target message to edit",
        when="When to post (now or yyyy-mm-dd hh:mm in WET, optional)",
        color="Embed color (hex, optional, default 00ffee)"
    )
    async def embededit(
        self,
        interaction: discord.Interaction,
        newtitle: str = None,
        source_channel: discord.TextChannel = None,
        message_id: str = None,
        target_channel: discord.TextChannel = None,
        target_message_id: str = None,
        when: str = "now",
        color: str = "00ffee"
    ):
        if interaction.user.id != settings.BOT_OWNER_ID:
            await interaction.response.send_message("Only the owner can use this command.", ephemeral=True)
            return

        # Fetch the source message
        try:
            msg = await source_channel.fetch_message(int(message_id))
        except Exception as e:
            await interaction.response.send_message(f"Could not fetch message: {e}", ephemeral=True)
            return

        embed_color = int(color, 16) if color else 0x00ffee
        embed = discord.Embed(
            title=newtitle if newtitle else None,
            description=msg.content,
            color=embed_color
        )
        if msg.attachments:
            embed.set_image(url=msg.attachments[0].url)

        if when.lower() == "now":
            # Edit the existing message
            try:
                target_msg = await target_channel.fetch_message(int(target_message_id))
                await target_msg.edit(embed=embed)
                await interaction.response.send_message("Embed edited.", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"Could not edit message: {e}", ephemeral=True)
        else:
            # Schedule the edit
            try:
                dt = datetime.strptime(when, "%Y-%m-%d %H:%M")
                dt = TIMEZONE.localize(dt)
            except Exception:
                await interaction.response.send_message("Invalid timestamp format. Use yyyy-mm-dd hh:mm", ephemeral=True)
                return
            schedules = load_schedules()
            schedules.append({
                "edit": True,
                "title": newtitle,
                "description": msg.content,
                "image": msg.attachments[0].url if msg.attachments else None,
                "color": color,
                "target_channel_id": target_channel.id,
                "target_message_id": target_message_id,
                "when": dt.isoformat(),
                "author_id": interaction.user.id
            })
            save_schedules(schedules)
            await interaction.response.send_message("Embed edit scheduled.", ephemeral=True)

    @tasks.loop(minutes=1)
    async def check_scheduled_embeds(self):
        now = datetime.now(TIMEZONE)
        schedules = load_schedules()
        to_run = []
        remaining = []
        for item in schedules:
            when = datetime.fromisoformat(item["when"])
            if when <= now:
                to_run.append(item)
            else:
                remaining.append(item)
        for item in to_run:
            channel = self.bot.get_channel(item["target_channel_id"])
            if not channel:
                continue
            embed_color = int(item.get("color", "00ffee"), 16)
            embed = discord.Embed(
                title=item.get("title"),
                description=item.get("description"),
                color=embed_color
            )
            if item.get("image"):
                embed.set_image(url=item["image"])
            if item.get("edit"):
                try:
                    msg = await channel.fetch_message(int(item["target_message_id"]))
                    await msg.edit(embed=embed)
                except Exception:
                    pass
            else:
                await channel.send(embed=embed)
        if to_run:
            save_schedules(remaining)

    async def cog_load(self):
        guild = discord.Object(id=settings.GUILD_ID)
        self.bot.tree.add_command(self.embed, guild=guild)
        self.bot.tree.add_command(self.embededit, guild=guild)

async def setup(bot):
    await bot.add_cog(EmbedManager(bot))