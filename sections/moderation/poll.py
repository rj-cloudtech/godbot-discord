from discord.ext import commands
import discord
from discord import app_commands
import asyncio
import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import json
import os
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class Poll(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.max_options = 20
        self.letter_emojis = [chr(0x1F1E6 + i) for i in range(26)]  # 🇦..🇿
        self.storage_path = Path(__file__).resolve().parents[2] / "poll.json"
        self.storage_lock = asyncio.Lock()
        self.active_polls: Dict[int, Dict[str, Any]] = {}  # keyed by message_id
        # ensure file exists
        if not self.storage_path.exists():
            self.storage_path.write_text(json.dumps({"polls": []}, indent=2), encoding="utf-8")
        # start background watcher after bot is ready
        bot.loop.create_task(self._start_on_ready_tasks())

    async def _start_on_ready_tasks(self):
        await self.bot.wait_until_ready()
        await self._load_and_schedule_polls()
        # watcher ensures polls that expire while bot is online or on restart are closed
        self.bot.loop.create_task(self._poll_watcher())

    def parse_date_time(self, date_str: str, time_str: str) -> datetime.datetime:
        tz = ZoneInfo("Europe/Amsterdam")
        try:
            d = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Date must be YYYY-MM-DD")
        t = None
        for fmt in ("%H:%M", "%I:%M%p", "%I:%M %p"):
            try:
                t = datetime.datetime.strptime(time_str.strip(), fmt).time()
                break
            except ValueError:
                continue
        if t is None:
            raise ValueError("Time must be HH:MM (24h) or H:MMam/pm")
        return datetime.datetime(d.year, d.month, d.day, t.hour, t.minute, tzinfo=tz)

    async def _load_storage(self) -> Dict[str, Any]:
        async with self.storage_lock:
            data = {"polls": []}
            try:
                text = self.storage_path.read_text(encoding="utf-8")
                data = json.loads(text)
            except Exception:
                # recreate if corrupted
                self.storage_path.write_text(json.dumps({"polls": []}, indent=2), encoding="utf-8")
            return data

    async def _save_storage(self, data: Dict[str, Any]):
        async with self.storage_lock:
            tmp = self.storage_path.with_suffix(".tmp")
            tmp.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
            os.replace(tmp, self.storage_path)

    async def _load_and_schedule_polls(self):
        data = await self._load_storage()
        now = datetime.datetime.now(tz=ZoneInfo("Europe/Amsterdam"))
        for p in data.get("polls", []):
            try:
                end_dt = datetime.datetime.fromisoformat(p["end"])
            except Exception:
                continue
            msg_id = int(p["message_id"])
            # register in-memory
            self.active_polls[msg_id] = p
            # schedule immediate close if past
            if end_dt <= now:
                logger.info(f"Scheduling immediate close for poll {msg_id} (expired while offline)")
                self.bot.loop.create_task(self._close_poll(p))
            else:
                self.bot.loop.create_task(self._schedule_close(p, end_dt))

    async def _schedule_close(self, poll: Dict[str, Any], end_dt: datetime.datetime):
        now = datetime.datetime.now(tz=ZoneInfo("Europe/Amsterdam"))
        wait_seconds = (end_dt - now).total_seconds()
        if wait_seconds > 0:
            try:
                await asyncio.sleep(wait_seconds)
            except asyncio.CancelledError:
                return
        await self._close_poll(poll)

    async def _poll_watcher(self):
        while True:
            try:
                data = await self._load_storage()
                now = datetime.datetime.now(tz=ZoneInfo("Europe/Amsterdam"))
                for p in list(data.get("polls", [])):
                    try:
                        end_dt = datetime.datetime.fromisoformat(p["end"])
                    except Exception:
                        continue
                    if end_dt <= now:
                        # avoid duplicate closes by checking active_polls
                        await self._close_poll(p)
                await asyncio.sleep(30)
            except Exception:
                await asyncio.sleep(30)

    @app_commands.command(name="poll", description="Create a timed poll")
    @app_commands.describe(
        question="The poll question",
        answers="Comma-separated answers, e.g. Yes,No,Maybe",
        end_date="End date in yyyy-mm-dd (Amsterdam timezone)",
        end_time="End time (HH:MM or H:MMam/pm) in Amsterdam time",
        multiple="Allow multiple answers"
    )
    async def poll(
        self,
        interaction: discord.Interaction,
        question: str,
        answers: str,
        end_date: str,
        end_time: str,
        multiple: bool = False,
    ):
        # parse and validate
        try:
            end_dt = self.parse_date_time(end_date, end_time)
        except ValueError as e:
            await interaction.response.send_message(f"Invalid date/time: {e}", ephemeral=True)
            return

        now = datetime.datetime.now(tz=ZoneInfo("Europe/Amsterdam"))
        min_delta = datetime.timedelta(minutes=1)
        # max duration removed to allow indefinite polls

        if end_dt <= now:
            await interaction.response.send_message("End time must be in the future (Amsterdam time).", ephemeral=True)
            return
        if end_dt - now < min_delta:
            await interaction.response.send_message("End time must be at least 1 minute in the future.", ephemeral=True)
            return

        opts = [a.strip() for a in answers.split(",") if a.strip()]
        if len(opts) < 2:
            await interaction.response.send_message("Provide at least two answers separated by commas.", ephemeral=True)
            return
        if len(opts) > self.max_options:
            await interaction.response.send_message(f"Max {self.max_options} answers allowed.", ephemeral=True)
            return
        if len(opts) > len(self.letter_emojis):
            await interaction.response.send_message("Too many options.", ephemeral=True)
            return

        embed = discord.Embed(title=f"Poll: {question}", colour=discord.Colour.blurple())
        embed.add_field(name="Ends (Europe/Amsterdam)", value=end_dt.strftime("%Y-%m-%d %H:%M %Z"), inline=False)
        embed.add_field(name="Multiple answers allowed", value=str(bool(multiple)), inline=False)
        desc_lines = []
        for i, opt in enumerate(opts):
            desc_lines.append(f"{self.letter_emojis[i]}  {opt}")
        embed.add_field(name="Options", value="\n".join(desc_lines), inline=False)
        embed.set_footer(text=f"Poll created by {interaction.user}")

        await interaction.response.send_message(embed=embed)
        msg = await interaction.original_response()

        for i in range(len(opts)):
            try:
                await msg.add_reaction(self.letter_emojis[i])
            except Exception:
                pass

        poll_record = {
            "message_id": msg.id,
            "channel_id": msg.channel.id,
            "guild_id": getattr(msg.guild, "id", None),
            "author_id": interaction.user.id,
            "question": question,
            "options": opts,
            "end": end_dt.isoformat(),
            "multiple": bool(multiple),
            "created": datetime.datetime.now(tz=ZoneInfo("Europe/Amsterdam")).isoformat()
        }

        # store and schedule
        data = await self._load_storage()
        data.setdefault("polls", []).append(poll_record)
        await self._save_storage(data)
        self.active_polls[msg.id] = poll_record
        self.bot.loop.create_task(self._schedule_close(poll_record, end_dt))

    async def _pop_poll_from_storage(self, message_id: int):
        """Atomically remove poll from storage and return it (or None if missing)."""
        async with self.storage_lock:
            try:
                text = self.storage_path.read_text(encoding="utf-8")
                data = json.loads(text)
            except Exception:
                # ensure file exists and return None
                self.storage_path.write_text(json.dumps({"polls": []}, indent=2), encoding="utf-8")
                return None

            polls = data.get("polls", [])
            remaining = []
            found = None
            for p in polls:
                try:
                    if int(p.get("message_id", -1)) == message_id:
                        found = p
                    else:
                        remaining.append(p)
                except Exception:
                    remaining.append(p)

            if found:
                data["polls"] = remaining
                tmp = self.storage_path.with_suffix(".tmp")
                tmp.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
                os.replace(tmp, self.storage_path)
                logger.info(f"Popped poll {message_id} from storage")

            return found

    async def _close_poll(self, poll: Dict[str, Any]):
        msg_id = int(poll["message_id"])

        # Atomically remove the poll from persistent storage so only one task closes it.
        stored = await self._pop_poll_from_storage(msg_id)
        if stored is None:
            # already closed / removed
            logger.debug(f"Poll {msg_id} already closed or missing in storage")
            self.active_polls.pop(msg_id, None)
            return
        # use the stored record (safer if passed 'poll' was stale)
        poll = stored
        # remove from in-memory map
        self.active_polls.pop(msg_id, None)
        logger.info(f"Closing poll {msg_id}")

        channel_id = int(poll["channel_id"])
        opts: List[str] = poll.get("options", [])
        multiple: bool = bool(poll.get("multiple", False))
        end_dt = datetime.datetime.fromisoformat(poll["end"])

        # fetch message
        try:
            channel = self.bot.get_channel(channel_id) or await self.bot.fetch_channel(channel_id)
            msg = await channel.fetch_message(msg_id)
        except Exception:
            # message gone; nothing else to do
            return

        counts = [0] * len(opts)
        votes_by_user = {}
        for i in range(len(opts)):
            emoji = self.letter_emojis[i]
            reaction = discord.utils.get(msg.reactions, emoji=emoji)
            if not reaction:
                continue
            try:
                users = [u async for u in reaction.users()]
            except Exception:
                continue
            for u in users:
                if u.bot:
                    continue
                votes_by_user.setdefault(u.id, []).append(i)

        if multiple:
            for choices in votes_by_user.values():
                for c in choices:
                    counts[c] += 1
        else:
            for choices in votes_by_user.values():
                if len(choices) == 1:
                    counts[choices[0]] += 1

        total_votes = sum(counts)
        res_embed = discord.Embed(title="Poll Results", colour=discord.Colour.green())
        res_embed.add_field(name="Question", value=poll.get("question", "Unknown"), inline=False)
        res_lines = []
        for i, opt in enumerate(opts):
            pct = (counts[i] / total_votes * 100) if total_votes > 0 else 0
            res_lines.append(f"{self.letter_emojis[i]} {opt} — {counts[i]} vote(s) ({pct:.1f}%)")
        res_embed.add_field(name="Results", value="\n".join(res_lines) or "No votes", inline=False)
        res_embed.set_footer(text=f"Closed at {end_dt.strftime('%Y-%m-%d %H:%M %Z')}")

        try:
            await msg.channel.send(embed=res_embed)
            if msg.embeds:
                closed_embed = msg.embeds[0]
                closed_embed.title = f"(CLOSED) {closed_embed.title}"
                await msg.edit(embed=closed_embed)
        except Exception:
            pass

        # storage already updated by _pop_poll_from_storage; nothing else to do

async def setup(bot):
    await bot.add_cog(Poll(bot))