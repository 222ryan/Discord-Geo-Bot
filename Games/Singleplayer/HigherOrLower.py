import asyncio

import discord
from discord.ext import commands
from ruamel.yaml import YAML
from System.events import geo

import KumosLab.create
import KumosLab.get
import random
import KumosLab.set
import KumosLab.data
import KumosLab.add

yaml = YAML()
with open("Configs/config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)


class HigherOrLower(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def hol(self, ctx):
        # higher or lower
        data_search = geo.find_one(
            {'player_id': ctx.author.id, "guild": ctx.guild.id, "game_type": {"$exists": True}})

        if data_search:
            if data_search['game_type'] != "hol":
                return
            category_id = await KumosLab.get.gameCategory(guild=ctx.guild)
            category = discord.utils.get(ctx.guild.categories, id=int(category_id))
            channel_id = data_search['channel_id']
            channel = discord.utils.get(category.channels, id=int(channel_id))
            db_search = geo.find_one({"Bot": True, "Maintenance": {"$exists": True}})
            if db_search["Maintenance"] is True:
                await ctx.reply("⚒️ The bot is currently under maintenance. The bot will return within **10** minutes.")
                await asyncio.sleep(10)
                await channel.delete()
                geo.delete_one(
                    {'player_id': ctx.author.id, "guild": ctx.guild.id, "game_type": {"$exists": True}})
                return
            if channel.id == ctx.message.channel.id:
                embed = discord.Embed(title="`🌎` GET READY, THE GAME BEGINS IN 3 SECONDS! YOU HAVE 5 MINUTES!")
                messsage = await channel.send(embed=embed)
                await asyncio.sleep(3)
                await messsage.delete()
            multiplier_chance = random.randint(1, 100)
            if multiplier_chance >= 90:
                coins_per_round = config['higher_lower_coins_per_correct_answer'] * 2
                await channel.send("`💸` **MULTIPLIER ACTIVATED! THIS ROUND HAS A MULTIPLIER OF x2 REWARDS!**")
            else:
                coins_per_round = config['higher_lower_coins_per_correct_answer']
            state = 0
            correct = 0
            if correct < 1:
                embed = discord.Embed(title=f"`🌎` HIGHER OR LOWER | {correct} CORRECT | 0 🪙",
                                      description="```Loading game...```")
                message = await channel.send(embed=embed)
            else:
                embed = discord.Embed(
                    title=f"`🌎` HIGHER OR LOWER | {correct} CORRECT | {coins_per_round * correct:,} 🪙",
                    description="```Loading game...```")
                message = await channel.send(embed=embed)
            await message.add_reaction("⬆️")
            await message.add_reaction("⬇️")
            await KumosLab.set.gameMessage(guild=ctx.guild, user=ctx.author, id=message.id)
            while state < 1:
                message = await KumosLab.get.gameMessage(guild=ctx.guild, user=ctx.author)
                message = await ctx.fetch_message(message)
                member = data_search['player_id']
                member = await self.client.fetch_user(member)
                random_country = await KumosLab.data.alldata()
                countries = []
                for i in random_country:
                    countries.append(i[0])
                if correct < 1:
                    await KumosLab.set.gameData(guild=ctx.guild, user=ctx.author, data=random.choice(countries))
                    last_country = await KumosLab.get.gameData(guild=ctx.guild, user=ctx.author)
                    countries.remove(last_country)
                else:
                    last_country = await KumosLab.get.gameData(guild=ctx.guild, user=ctx.author)
                country_2 = random.choice(countries)
                country_1_size = await KumosLab.data.sizedata(country=last_country)
                country_2_size = await KumosLab.data.sizedata(country=country_2)
                if correct < 1:
                    embed.title = f"`🌎` HIGHER OR LOWER | {correct} CORRECT | {coins_per_round * correct:,} 🪙"
                    embed.description = f"`Which country is bigger?\n{last_country} | {country_2}`"
                    embed.add_field(name=f"{last_country}", value=f"```{country_1_size:,}km²```", inline=False)
                    embed.add_field(name=f"{country_2}", value=f"```    ⬆️       "
                                                               f"       OR       "
                                                               f"       ⬇️    ```", inline=True)
                else:
                    embed.title = f"`🌎` HIGHER OR LOWER | {correct} CORRECT | {coins_per_round * correct:,} 🪙"
                    embed.description = f"`Which country is bigger?\n{last_country} | {country_2}`"
                    embed.set_field_at(index=0, name=f"{last_country}", value=f"```{country_1_size:,}km²```",
                                       inline=False)
                    embed.set_field_at(index=1, name=f"{country_2}", value=f"```    ⬆️       "
                                                                           f"       OR       "
                                                                           f"       ⬇️    ```", inline=True)

                embed.set_thumbnail(url=await KumosLab.data.flagdata(country=last_country))
                embed.set_footer(text=f"{coins_per_round:,}🪙's per correct answer!")
                await message.edit(embed=embed)

                def check(reaction, user):
                    return user == member and str(reaction.emoji) in ['⬆️', '⬇️']

                try:
                    reaction, user = await self.client.wait_for('reaction_add', timeout=300.0, check=check)

                    if str(reaction.emoji) == '⬆️':
                        if int(country_2_size) > int(country_1_size):
                            correct += 1
                            highscore = await KumosLab.get.holHighScore(guild=ctx.guild, user=ctx.author)
                            if correct > highscore:
                                await KumosLab.add.holHighScore(guild=ctx.guild, user=ctx.author, amount=1)
                            await KumosLab.set.gameData(guild=ctx.guild, user=ctx.author, data=str(country_2))
                            await KumosLab.add.coins(guild=ctx.guild, user=ctx.author,
                                                     amount=coins_per_round)
                            await KumosLab.add.holWins(guild=ctx.guild, user=ctx.author, amount=1)
                            await message.remove_reaction(reaction.emoji, member)
                        elif int(country_2_size) < int(country_1_size):
                            state += 1
                            await KumosLab.add.holLosses(guild=ctx.guild, user=ctx.author, amount=1)
                            embed = discord.Embed(title="`🌎` INCORRECT",
                                                  description=f"You answered incorrectly.")
                            embed.add_field(name=f"{last_country}", value=f"```{country_1_size:,}km²```", inline=False)
                            embed.add_field(name=f"{country_2}", value=f"```{country_2_size:,}km²```", inline=False)
                            embed.add_field(name="Coins Earned", value=f"```{coins_per_round * correct:,}🪙```")
                            await channel.send(embed=embed)
                            embed = discord.Embed(title="`🌎` Play Again?",
                                                  description="```Do you want to play again?```")
                            message = await channel.send(embed=embed)
                            await message.add_reaction("✅")
                            await message.add_reaction("❌")

                            def check(reaction, user):
                                return user == ctx.author and reaction.message.id == message.id

                            try:
                                reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=30)
                            except asyncio.TimeoutError:
                                await channel.delete()
                                geo.delete_one(
                                    {'player_id': ctx.author.id, "guild": ctx.guild.id, "game_type": {"$exists": True}})
                                return
                            else:
                                if str(reaction.emoji) == "✅":
                                    await self.hol(ctx)
                                elif str(reaction.emoji) == "❌":
                                    await channel.delete()
                                    geo.delete_one(
                                        {'player_id': ctx.author.id, "guild": ctx.guild.id,
                                         "game_type": {"$exists": True}})
                                    return

                    if str(reaction.emoji) == '⬇️':
                        if int(country_1_size) > int(country_2_size):
                            correct += 1
                            highscore = await KumosLab.get.holHighScore(guild=ctx.guild, user=ctx.author)
                            if correct > highscore:
                                await KumosLab.add.holHighScore(guild=ctx.guild, user=ctx.author, amount=1)
                            await KumosLab.set.gameData(guild=ctx.guild, user=ctx.author, data=str(country_2))
                            await KumosLab.add.coins(guild=ctx.guild, user=ctx.author, amount=coins_per_round)
                            await KumosLab.add.holWins(guild=ctx.guild, user=ctx.author, amount=1)
                            await message.remove_reaction(reaction.emoji, member)
                        elif int(country_1_size) < int(country_2_size):
                            state += 1
                            await KumosLab.add.holLosses(guild=ctx.guild, user=ctx.author, amount=1)
                            embed = discord.Embed(title="`🌎` INCORRECT",
                                                  description=f"You answered incorrectly.")
                            embed.add_field(name=f"{last_country}", value=f"```{country_1_size:,}km²```", inline=False)
                            embed.add_field(name=f"{country_2}", value=f"```{country_2_size:,}km²```", inline=False)
                            embed.add_field(name="Coins Earned", value=f"```{coins_per_round * correct:,}🪙```")
                            await channel.send(embed=embed)
                            embed = discord.Embed(title="`🌎` Play Again?",
                                                  description="```Do you want to play again?```")
                            message = await channel.send(embed=embed)
                            await message.add_reaction("✅")
                            await message.add_reaction("❌")

                            def check(reaction, user):
                                return user == ctx.author and reaction.message.id == message.id

                            try:
                                reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=30)
                            except asyncio.TimeoutError:
                                await channel.delete()
                                geo.delete_one(
                                    {'player_id': ctx.author.id, "guild": ctx.guild.id, "game_type": {"$exists": True}})
                                return
                            else:
                                if str(reaction.emoji) == "✅":
                                    await self.hol(ctx)
                                elif str(reaction.emoji) == "❌":
                                    await channel.delete()
                                    geo.delete_one(
                                        {'player_id': ctx.author.id, "guild": ctx.guild.id,
                                         "game_type": {"$exists": True}})
                                    return
                except asyncio.TimeoutError:
                    embed = discord.Embed(title="`🌎` TIME IS UP!",
                                          description=f"The game has ended.")
                    embed.add_field(name=f"{last_country}", value=f"```{country_1_size:,}km²```", inline=False)
                    embed.add_field(name=f"{country_2}", value=f"```{country_2_size:,}km²```", inline=False)
                    embed.add_field(name="Coins Earned", value=f"```{coins_per_round * correct:,}🪙```")
                    await channel.send(embed=embed)
                    embed = discord.Embed(title="`🌎` Play Again?",
                                          description="```Do you want to play again?```")
                    message = await channel.send(embed=embed)
                    await message.add_reaction("✅")
                    await message.add_reaction("❌")

                    def check(reaction, user):
                        return user == ctx.author and reaction.message.id == message.id

                    try:
                        reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=30)
                    except asyncio.TimeoutError:
                        await channel.delete()
                        geo.delete_one(
                            {'player_id': ctx.author.id, "guild": ctx.guild.id, "game_type": {"$exists": True}})
                        return
                    else:
                        if str(reaction.emoji) == "✅":
                            await self.hol(ctx)
                        elif str(reaction.emoji) == "❌":
                            await channel.delete()
                            geo.delete_one(
                                {'player_id': ctx.author.id, "guild": ctx.guild.id,
                                 "game_type": {"$exists": True}})
                            return


def setup(client):
    client.add_cog(HigherOrLower(client))
