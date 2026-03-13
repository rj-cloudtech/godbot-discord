import discord
from discord.ext import commands
from discord import app_commands
import os
import json
from datetime import datetime, timedelta
import asyncio

import settings

COURTROOM_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "courtroom_cases.json")
GENERAL_CHANNEL_ID = settings.GENERAL_CHANNEL_ID  # Set this in your settings.py

def load_cases():
    if not os.path.exists(COURTROOM_FILE):
        with open(COURTROOM_FILE, "w") as f:
            json.dump([], f)
    with open(COURTROOM_FILE, "r") as f:
        return json.load(f)

def save_cases(cases):
    with open(COURTROOM_FILE, "w") as f:
        json.dump(cases, f, indent=4)

class Courtroom(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pending_cases = []

    async def cog_load(self):
        # On cog load, reload pending cases and re-add reactions if needed
        await self.restore_cases()

    async def restore_cases(self):
        cases = load_cases()
        now = datetime.utcnow().timestamp()
        for case in cases:
            if not case.get("resolved", False):
                # Re-add reactions if message still exists and not resolved
                guild = self.bot.get_guild(case["guild_id"])
                if not guild:
                    continue
                channel = guild.get_channel(case["channel_id"])
                if not channel:
                    continue
                try:
                    msg = await channel.fetch_message(case["message_id"])
                except Exception:
                    continue
                # Add reactions if not already present
                try:
                    await msg.add_reaction("⚖️")
                    await msg.add_reaction("👩‍⚖️")
                except Exception:
                    pass
                # If 24h passed, select volunteers
                if now >= case["created_at"] + 24 * 3600 and not case.get("volunteers_selected"):
                    await self.select_volunteers(case, msg)
        self.pending_cases = cases

    @app_commands.command(name="sue", description="Sue a member for a reason in the fantasy courtroom.")
    @app_commands.describe(who="Who do you want to sue?", why="Why are you suing them?")
    async def sue(self, interaction: discord.Interaction, who: discord.Member, why: str):
        if who.id == interaction.user.id:
            await interaction.response.send_message("You can't sue yourself!", ephemeral=True)
            return

        guild = interaction.guild
        channel = guild.get_channel(GENERAL_CHANNEL_ID)
        if not channel:
            await interaction.response.send_message("General channel not found.", ephemeral=True)
            return

        embed = discord.Embed(
            title="Fantasy Courtroom Case",
            description=(
                f"**{who.mention}** is being sued by **{interaction.user.mention}**.\n"
                f"**Reason:** {why}\n\n"
                f"We are looking for a **Judge** and **Jury**.\n"
                f"Volunteer by clicking on the emojis below!\n"
                f"👩‍⚖️ for Judge\n⚖️ for Jury\n\n"
                f"A volunteer will be selected after 24 hours."
            ),
            color=discord.Color.gold(),
            timestamp=datetime.utcnow()
        )
        msg = await channel.send(embed=embed)
        await msg.add_reaction("👩‍⚖️")  # Judge
        await msg.add_reaction("⚖️")    # Jury

        # Save case info for persistence
        case = {
            "guild_id": guild.id,
            "channel_id": channel.id,
            "message_id": msg.id,
            "plaintiff_id": interaction.user.id,
            "defendant_id": who.id,
            "reason": why,
            "created_at": datetime.utcnow().timestamp(),
            "resolved": False,
            "volunteers_selected": False
        }
        cases = load_cases()
        cases.append(case)
        save_cases(cases)
        self.pending_cases = cases

        await interaction.response.send_message("Your case has been submitted to the courtroom!", ephemeral=True)

    async def select_volunteers(self, case, msg):
        # Fetch reactions and select random judge and jury
        try:
            await msg.fetch()
        except Exception:
            return
        judge_users = []
        jury_users = []
        for reaction in msg.reactions:
            if str(reaction.emoji) == "👩‍⚖️":
                async for user in reaction.users():
                    if not user.bot:
                        judge_users.append(user)
            elif str(reaction.emoji) == "⚖️":
                async for user in reaction.users():
                    if not user.bot:
                        jury_users.append(user)
        judge = random.choice(judge_users) if judge_users else None
        jury = random.choice(jury_users) if jury_users else None

        summary = "Volunteers selected:\n"
        if judge:
            summary += f"👩‍⚖️ Judge: {judge.mention}\n"
        else:
            summary += "👩‍⚖️ Judge: No volunteers\n"
        if jury:
            summary += f"⚖️ Jury: {jury.mention}\n"
        else:
            summary += "⚖️ Jury: No volunteers\n"

        await msg.reply(summary)
        case["volunteers_selected"] = True
        case["resolved"] = True
        cases = load_cases()
        for c in cases:
            if c["message_id"] == case["message_id"]:
                c.update(case)
        save_cases(cases)

async def setup(bot):
    await bot.add_cog(Courtroom(bot))