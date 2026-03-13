import discord
from discord.ext import commands
from discord import app_commands
import random
import os
import json
import settings

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data.json")

def load_data():
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        with open(DATA_FILE, "w") as f:
            json.dump({"wallets": {}}, f)
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        with open(DATA_FILE, "w") as f:
            json.dump({"wallets": {}}, f)
        return {"wallets": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class RockPaperScissors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_challenges = {}  # {challenged_id: (challenger_id, amount)}

    @app_commands.command(name="rockpaperscissors", description="Play Rock Paper Scissors against the bot or another member!")
    @app_commands.describe(
        amount="The amount to play with",
        opponent="Mention a member to challenge, or leave empty to play against the bot"
    )
    async def rockpaperscissors(self, interaction: discord.Interaction, amount: int, opponent: discord.Member = None):
        user_id = str(interaction.user.id)
        data = load_data()
        wallets = data.setdefault("wallets", {})
        balance = wallets.get(user_id, 0)

        if amount <= 0:
            await interaction.response.send_message("You must play with a positive amount.", ephemeral=True)
            return
        if balance < amount:
            await interaction.response.send_message(f"You don't have enough {settings.CURRENCY_NAME} to play for that amount.", ephemeral=True)
            return

        if opponent is None or opponent.bot:
            # Play against bot
            await interaction.response.send_message("Choose: rock, paper, or scissors (type your choice below).", ephemeral=False)

            def check(m):
                return m.author.id == interaction.user.id and m.channel == interaction.channel and m.content.lower() in ["rock", "paper", "scissors"]

            try:
                msg = await self.bot.wait_for("message", check=check, timeout=30)
            except asyncio.TimeoutError:
                await interaction.followup.send("Timed out! You didn't choose in time.", ephemeral=True)
                return

            user_choice = msg.content.lower()
            bot_choice = random.choice(["rock", "paper", "scissors"])

            result = self.determine_winner(user_choice, bot_choice)
            if result == "win":
                wallets[user_id] = balance + amount
                result_msg = f"🪨📄✂️ You chose **{user_choice}**. Bot chose **{bot_choice}**. You win {amount} {settings.CURRENCY_NAME}!"
            elif result == "lose":
                wallets[user_id] = balance - amount
                result_msg = f"🪨📄✂️ You chose **{user_choice}**. Bot chose **{bot_choice}**. You lose {amount} {settings.CURRENCY_NAME}."
            else:
                result_msg = f"🪨📄✂️ You chose **{user_choice}**. Bot chose **{bot_choice}**. It's a tie! No money lost."

            save_data(data)
            await interaction.followup.send(result_msg, ephemeral=False)
        else:
            # Challenge another member
            if opponent.id == interaction.user.id:
                await interaction.response.send_message("You can't challenge yourself!", ephemeral=True)
                return

            opp_id = str(opponent.id)
            opp_balance = wallets.get(opp_id, 0)
            if opp_balance < amount:
                await interaction.response.send_message(f"{opponent.mention} doesn't have enough {settings.CURRENCY_NAME} to play for that amount.", ephemeral=True)
                return

            self.active_challenges[opp_id] = (user_id, amount)
            await interaction.response.send_message(
                f"{opponent.mention}, you have been challenged to Rock Paper Scissors by {interaction.user.mention} for {amount} {settings.CURRENCY_NAME}!\n"
                f"Type `rock`, `paper`, or `scissors` in this channel to accept and play, or type `no` to decline. You have 5 minutes.",
                ephemeral=False
            )

            def check(m):
                return (
                    m.author.id == opponent.id and
                    m.channel == interaction.channel and
                    (m.content.lower() in ["rock", "paper", "scissors", "no"])
                )

            try:
                msg = await self.bot.wait_for("message", check=check, timeout=300)  # 5 minutes
            except asyncio.TimeoutError:
                await interaction.followup.send(f"{opponent.mention} did not respond in time. Challenge cancelled.", ephemeral=False)
                self.active_challenges.pop(opp_id, None)
                return

            if msg.content.lower() == "no":
                await interaction.followup.send(f"{opponent.mention} declined the challenge. Game cancelled.", ephemeral=False)
                self.active_challenges.pop(opp_id, None)
                return

            opp_choice = msg.content.lower()
            await interaction.followup.send(f"{interaction.user.mention}, type `rock`, `paper`, or `scissors` to play your move.", ephemeral=False)

            def challenger_check(m):
                return (
                    m.author.id == interaction.user.id and
                    m.channel == interaction.channel and
                    m.content.lower() in ["rock", "paper", "scissors"]
                )

            try:
                challenger_msg = await self.bot.wait_for("message", check=challenger_check, timeout=30)
            except asyncio.TimeoutError:
                await interaction.followup.send(f"{interaction.user.mention} did not respond in time. Challenge cancelled.", ephemeral=False)
                self.active_challenges.pop(opp_id, None)
                return

            challenger_choice = challenger_msg.content.lower()

            result = self.determine_winner(challenger_choice, opp_choice)
            if result == "win":
                wallets[user_id] = balance + amount
                wallets[opp_id] = opp_balance - amount
                result_msg = (
                    f"{interaction.user.mention} chose **{challenger_choice}**\n"
                    f"{opponent.mention} chose **{opp_choice}**\n"
                    f"{interaction.user.mention} wins {amount} {settings.CURRENCY_NAME}!"
                )
            elif result == "lose":
                wallets[user_id] = balance - amount
                wallets[opp_id] = opp_balance + amount
                result_msg = (
                    f"{interaction.user.mention} chose **{challenger_choice}**\n"
                    f"{opponent.mention} chose **{opp_choice}**\n"
                    f"{opponent.mention} wins {amount} {settings.CURRENCY_NAME}!"
                )
            else:
                result_msg = (
                    f"{interaction.user.mention} chose **{challenger_choice}**\n"
                    f"{opponent.mention} chose **{opp_choice}**\n"
                    f"It's a tie! No money lost."
                )

            save_data(data)
            await interaction.followup.send(result_msg, ephemeral=False)
            self.active_challenges.pop(opp_id, None)

    def determine_winner(self, user, opponent):
        if user == opponent:
            return "tie"
        if (
            (user == "rock" and opponent == "scissors") or
            (user == "paper" and opponent == "rock") or
            (user == "scissors" and opponent == "paper")
        ):
            return "win"
        return "lose"

async def setup(bot):
    await bot.add_cog(RockPaperScissors(bot))