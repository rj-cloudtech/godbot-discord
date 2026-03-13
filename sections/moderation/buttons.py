# Example: Role buttons with toggle
import discord
from discord.ext import commands
from discord import app_commands

ROLE_BUTTONS = [
    {"label": "God Bot", "role_id": 1380183599013429388},
    {"label": "CS Pro Scene", "role_id": 1416840484998873089},
    {"label": "Bonus channels", "role_id": 1416840541693284502},
]

class RoleButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        for btn in ROLE_BUTTONS:
            self.add_item(RoleButton(btn["label"], btn["role_id"]))

class RoleButton(discord.ui.Button):
    def __init__(self, label, role_id):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(self.role_id)
        if not role:
            await interaction.response.send_message("Role not found.", ephemeral=True)
            return
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"Role **{role.name}** removed.", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"Role **{role.name}** added.", ephemeral=True)

# Command to post the buttons
class RoleButtons(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.synced = False

    @app_commands.command(name="rolebuttons", description="Post role toggle buttons.")
    async def rolebuttons(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Click a button to toggle a role:", 
            view=RoleButtonView(),
            ephemeral=False
        )

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.synced:
            GUILD_ID = 1272065925016977433  # Replace with your actual guild ID
            await self.bot.tree.sync(guild=discord.Object(id=GUILD_ID))
            self.synced = True

async def setup(bot):
    await bot.add_cog(RoleButtons(bot))