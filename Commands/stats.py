import discord
from discord.ext import commands
from dotenv import load_dotenv
import KumosLab.get

load_dotenv()


class Stats(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name='stats', aliases=['profile', 'statistics'])
    async def stats(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        embed = discord.Embed(title=f"📊 - {member}'s Stats",
                              description=f"```{await KumosLab.get.coins(guild=ctx.guild, user=member):,}🪙 Coins```")
        embed.add_field(name="🎮 Game Stats",
                        value=f"```🏳️ Guess The Flag:\n- {await KumosLab.get.ntfwins(guild=ctx.guild, user=member)} Wins\n- {await KumosLab.get.ntflosses(guild=ctx.guild, user=member)} Losses"
                              f"\n\n⬆️ Higher Or Lower:\n- {await KumosLab.get.holWins(guild=ctx.guild, user=member)} Correct\n- {await KumosLab.get.holLosses(guild=ctx.guild, user=member)} Losses\n- {await KumosLab.get.holHighScore(guild=ctx.guild, user=member)} High Score"
                              f"\n\n🟩 Guess Shape:\n- {await KumosLab.get.gsWins(guild=ctx.guild, user=member)} Wins\n- {await KumosLab.get.gsLosses(guild=ctx.guild, user=member)} Losses\n- {await KumosLab.get.gsBestScore(guild=ctx.guild, user=member)} Best Score```")
        embed.set_thumbnail(url=member.avatar_url)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Stats(client))
