import asyncio

import discord
from discord.ext import commands
from dotenv import load_dotenv
from ruamel.yaml import YAML

from System.events import geo
import KumosLab.games
import KumosLab.data
import KumosLab.get
import KumosLab.add
import KumosLab.set

load_dotenv()
yaml = YAML()
with open("Configs/config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)


class FindMatch(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, category):
        game_category = await KumosLab.get.gameCategory(guild=category.guild)
        if category.id == game_category:
            category = await category.guild.create_category(name="🎮 | GEO GAMES")
            geo.update_one({"guildid": category.guild.id, "bot_type": "GeoBot-Server"},
                           {"$set": {"category": category.id}})

    @commands.command(name='findmatch', aliases=['fm', 'match', 'find', 'f'])
    async def findmatch(self, ctx, gameType: str = None):
        if gameType is None:
            gameType = "gsm"
        result = geo.find(
            {'host_id': {'$exists': True}, "guild": ctx.guild.id, "game_type": gameType.lower(), "state": "Waiting for Players..", "publicity": "public"})

        player_count = []
        host = []
        state = []

        embed = discord.Embed(title=f"🌎 PUBLIC GAMES FOR {gameType.upper()}")

        for x in result:
            player_count.append(x['player_count'])
            host.append(x['host_id'])
            state.append(x['state'])

        if len(host) < 1:
            embed.description = "```No Games Found!```"
            await ctx.send(embed=embed)


        pagination = list(zip(player_count, host, state))
        pages = [pagination[i:i + 10] for i in range(0, len(pagination), 10)]
        page = 0
        num = 0
        player_count_list = []
        host_list = []
        state_list = []
        for i in pages:
            embed.clear_fields()
            for player_count, host, state in i:
                user = self.client.get_user(host)
                num += 1
                embed.add_field(name=f"#{num}: {user}",
                                value=f"```Players: {player_count}/4\nGame State: {state}```", inline=True)
            embed.set_footer(text=f"Page {page + 1}/{len(pages)}")
            message = await ctx.send(embed=embed)
            page += 1
            if len(pages) > 1:
                await message.add_reaction("⬅")
                await message.add_reaction("➡")
            await message.add_reaction("❌")

            while True:
                def check(reaction, user):
                    return user == ctx.author and str(reaction.emoji) in ["⬅", "➡",
                                                                          "❌"] and reaction.message.id == message.id

                try:
                    reaction, user = await ctx.bot.wait_for("reaction_add", timeout=60.0, check=check)

                    if str(reaction.emoji) == "⬅":
                        if page == 1:
                            pass
                        else:
                            page -= 1
                            embed.clear_fields()
                            for player_count, host, state in pages[page - 1]:
                                user = self.client.get_user(host)
                                num -= 1
                                player_count_list.append(player_count)
                                host_list.append(host)
                                state_list.append(state)
                            for x in range(0, len(host_list)):
                                embed.add_field(name=f"#{x + 1 + num - len(host_list)}: {host_list[x]}",
                                                value=f"```Players: {player_count_list[x]}/4\nGame State: {state_list[x]}```", inline=True)
                            player_count_list.clear()
                            host_list.clear()
                            state_list.clear()
                            embed.set_footer(text=f"Page {page}/{len(pages)}")
                            await message.edit(embed=embed)
                            await message.remove_reaction("⬅", user)
                            await message.remove_reaction("➡", user)
                            await message.remove_reaction("❌", user)
                    elif str(reaction.emoji) == "➡":
                        if page == len(pages):
                            pass
                        else:
                            page += 1
                            embed.clear_fields()
                            for player_count, host, state in pages[page - 1]:
                                user = self.client.get_user(host)
                                num += 1
                                player_count_list.append(player_count)
                                host_list.append(host)
                                state_list.append(state)
                            for x in range(0, len(host_list)):
                                embed.add_field(name=f"#{x + 1 + num - len(host_list)}: {host_list[x]}",
                                                value=f"```Players: {player_count_list[x]}/4\nGame State: {state_list[x]}```", inline=True)
                            player_count_list.clear()
                            host_list.clear()
                            state_list.clear()
                            embed.set_footer(text=f"Page {page}/{len(pages)}")
                            await message.edit(embed=embed)
                            await message.remove_reaction("⬅", user)
                            await message.remove_reaction("➡", user)
                            await message.remove_reaction("❌", user)
                    elif str(reaction.emoji) == "❌":
                        await message.delete()
                        return
                except asyncio.TimeoutError:
                    await message.delete()
                    return




def setup(client):
    client.add_cog(FindMatch(client))
