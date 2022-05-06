from discord.ext import commands
from ruamel.yaml import YAML

import KumosLab.create

yaml = YAML()
with open("Configs/config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)


class Leaderboard(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['lb', 'leaders', 'rankings'])
    async def leaderboard(self, ctx,  game=None):
        await KumosLab.create.leaderboard(self=self, ctx=ctx, guild=ctx.guild, game=game)

def setup(client):
    client.add_cog(Leaderboard(client))