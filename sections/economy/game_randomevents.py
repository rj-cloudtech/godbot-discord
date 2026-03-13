from discord.ext import commands

class GameRandomEvents(commands.Cog):
    pass  # No code yet

async def setup(bot):
    await bot.add_cog(GameRandomEvents(bot))