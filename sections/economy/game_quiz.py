from discord.ext import commands

class GameQuiz(commands.Cog):
    pass  # No code yet

async def setup(bot):
    await bot.add_cog(GameQuiz(bot))