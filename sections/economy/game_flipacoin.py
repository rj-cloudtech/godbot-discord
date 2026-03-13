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

class FlipACoin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="flipacoin", description="Bet on a coin flip! 50/50 chance to double your money.")
    @app_commands.describe(
        amount="The amount to bet",
        choice="Your choice: heads or tails"
    )
    @app_commands.choices(choice=[
        app_commands.Choice(name="Heads", value="heads"),
        app_commands.Choice(name="Tails", value="tails")
    ])
    async def flipacoin(self, interaction: discord.Interaction, amount: int, choice: app_commands.Choice[str]):
        user_id = str(interaction.user.id)
        data = load_data()
        wallets = data.setdefault("wallets", {})
        balance = wallets.get(user_id, 0)

        if amount <= 0:
            await interaction.response.send_message("You must bet a positive amount.", ephemeral=True)
            return
        if balance < amount:
            await interaction.response.send_message(f"You don't have enough {settings.CURRENCY_NAME} to bet that amount.", ephemeral=True)
            return

        user_choice = choice.value.lower()
        flip_result = random.choice(["heads", "tails"])

        if user_choice == flip_result:
            winnings = amount
            wallets[user_id] = balance + winnings
            result_msg = f"🎉 It's **{flip_result.capitalize()}**! You won {winnings} {settings.CURRENCY_NAME}!\nYour new balance: {wallets[user_id]} {settings.CURRENCY_NAME}"
        else:
            wallets[user_id] = balance - amount
            result_msg = f"😢 It's **{flip_result.capitalize()}**. You lost {amount} {settings.CURRENCY_NAME}.\nYour new balance: {wallets[user_id]} {settings.CURRENCY_NAME}"

        save_data(data)
        await interaction.response.send_message(result_msg, ephemeral=False)

async def setup(bot):
    await bot.add_cog(FlipACoin(bot))