import asyncio
import os
import sqlite3

import discord
from ruamel.yaml import YAML
import KumosLab.conversion as conversion
from System.events import geo



yaml = YAML()
with open("Configs/config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)

async def leaderboard(self=None, ctx=None, guild=None, game='gtf'):
    if self is None:
        print("[Leaderboard-MongoDB] Self is None")
        return
    if ctx is None:
        print("[Leaderboard-MongoDB] Context is None")
        return
    if guild is None:
        print("[Leaderboard-MongoDB] Guild is None")
        return

    if game is None:
        game = 'ntf'
    if game == 'gtf':
        game = 'ntf'


    if game.lower() == "gtf" or game.lower() == "ntf":
        result = geo.find({"guildid": guild.id,"ntf_wins": {"$exists": True}}).sort(
            "ntf_wins", -1)
        embed = discord.Embed(title=f"🌎 Guess The Flag Leaderboard")
    elif game.lower() == "gs":
        result = geo.find({"guildid": guild.id,"gs_wins": {"$exists": True}}).sort(
            "gs_wins", -1)
        embed = discord.Embed(title=f"🌎 Guess The Shape Leaderboard")
    else:
        result = geo.find({"guildid": guild.id,"hol_wins": {"$exists": True}}).sort(
            "hol_wins", -1)
        embed = discord.Embed(title=f"🌎 Higher Or Lower Leaderboard")

    if result is None:
        print("Server Not Found!")

    users = []
    wins = []
    losses = []
    coins = []

    for x in result:
        users.append(x["username"])
        try:
            wins.append(x[f"{game}_wins"])
            losses.append(x[f"{game}_losses"])
        except Exception as e:
            embed = discord.Embed(title=f"🌎 Leaderboard Error", description="```That game is not supported!```")
            await ctx.send(embed=embed)
            return
        coins.append(x["coins"])

    pagination = list(zip(users, wins, losses, coins))
    pages = [pagination[i:i + 10] for i in range(0, len(pagination), 10)]
    page = 0
    num = 0
    user_list = []
    wins_list = []
    losses_list = []
    coins_list = []
    for i in pages:
        embed.clear_fields()
        for users, wins, losses, coins in i:
            num += 1
            embed.add_field(name=f"#{num}: {users}", value=f"```Coins: {coins:,}🪙\nWins: {wins}\nLosses: {losses}```", inline=True)
        embed.set_footer(text=f"Page {page + 1}/{len(pages)}")
        message = await ctx.send(embed=embed)
        page += 1
        if len(pages) > 1:
            await message.add_reaction("⬅")
            await message.add_reaction("➡")
        await message.add_reaction("❌")

        while True:
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["⬅", "➡", "❌"] and reaction.message.id == message.id

            try:
                reaction, user = await ctx.bot.wait_for("reaction_add", timeout=60.0, check=check)

                if str(reaction.emoji) == "⬅":
                    if page == 1:
                        pass
                    else:
                        page -= 1
                        embed.clear_fields()
                        for users, wins, losses, coins in pages[page - 1]:
                            num -= 1
                            user_list.append(users)
                            wins_list.append(wins)
                            losses_list.append(losses)
                            coins_list.append(coins)
                        for x in range(0, len(user_list)):
                            embed.add_field(name=f"#{x + 1 + num - len(user_list)}: {user_list[x]}",
                                            value=f"```Coins: {coins_list[x]:,}🪙\nWins: {wins_list[x]:,}\nLosses: {losses_list[x]:,}```", inline=True)
                        user_list.clear()
                        wins.clear()
                        losses_list.clear()
                        coins_list.clear()
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
                        for users, wins, losses, coins in pages[page - 1]:
                            num += 1
                            user_list.append(users)
                            wins_list.append(wins)
                            losses_list.append(losses)
                            coins_list.append(coins)
                        for x in range(0, len(user_list)):
                            embed.add_field(name=f"#{x + 1 + num - len(user_list)}: {user_list[x]}",
                                            value=f"```Coins: {coins_list[x]:,}🪙\nWins: {wins_list[x]:,}\nLosses: {losses_list[x]:,}```",
                                            inline=True)
                        user_list.clear()
                        wins_list.clear()
                        losses_list.clear()
                        coins_list.clear()
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
