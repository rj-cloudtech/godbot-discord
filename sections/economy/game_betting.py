from discord.ext import commands

class GameBetting(commands.Cog):
    pass  # No code yet

async def setup(bot):
    await bot.add_cog(GameBetting(bot))