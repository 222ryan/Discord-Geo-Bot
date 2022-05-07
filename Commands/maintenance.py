import asyncio

import discord
from discord.ext import commands
from ruamel.yaml import YAML
from System.events import geo
from main import status_loop

import KumosLab.create

yaml = YAML()
with open("Configs/config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)


class Maintenance(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['mm'])
    async def maintenance(self, ctx):
        if ctx.author.id == config["OwnerID"]:
            db_search = geo.find_one({"Bot": True, "Maintenance": {"$exists": True}})
            if db_search:
                status_loop.stop()
                geo.update_one({"Bot": True}, {"$set": {"Maintenance": True}})
                await self.client.change_presence(status=discord.Status.dnd, activity=discord.Game(name="⚒️ Maintenance Mode"))
                embed = discord.Embed(title="⚒️ Maintenance Mode", description="```Maintenance Mode has started.```")
                await ctx.reply(embed=embed)
            else:
                status_loop.stop()
                geo.insert_one({"Bot": True, "Maintenance": True})
                await self.client.change_presence(status=discord.Status.dnd, activity=discord.Game(name="⚒️ Maintenance Mode"))
                embed = discord.Embed(title="⚒️ Maintenance Mode", description="```Maintenance Mode has started.```")
                await ctx.reply(embed=embed)
        await asyncio.sleep(600)
        exit("Maintenance Mode has ended.")


def setup(client):
    client.add_cog(Maintenance(client))