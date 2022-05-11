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


class GuessTheFlag(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name='gtf')
    async def gtf(self, ctx):
        data_search = geo.find_one(
            {'player_id': ctx.author.id, "guild": ctx.guild.id, "game_type": {"$exists": True}})

        if data_search:
            if data_search['game_type'] != "gtf":
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
                embed = discord.Embed(title="`🌎` GET READY, THE GAME BEGINS IN 3 SECONDS! YOU HAVE 2 MINUTES TO "
                                            "COMPLETE THE GAME.")
                message = await channel.send(embed=embed)
                multiplier_chance = random.randint(1, 100)
                if multiplier_chance >= 90:
                    coins_per_round = config['ntf_coins_per_correct_answer'] * 2
                    coins_per_win = config['ntf_coins_per_game_win'] * 2
                    await channel.send("`💸` **MULTIPLIER ACTIVATED! THIS ROUND HAS A MULTIPLIER OF x2 REWARDS!**")
                else:
                    coins_per_round = config['ntf_coins_per_correct_answer']
                    coins_per_win = config['ntf_coins_per_game_win']
                await asyncio.sleep(3)
                await message.delete()

                round = 0
                embed = discord.Embed(title=f"`🌎` ROUND {round}/10")
                embed.add_field(name="ANSWERS",
                                value=f"```1️⃣ - Loading..\n2️⃣ - Loading..\n3️⃣ - Loading..\n4️⃣ - Loading..```")
                embed.set_footer(text=f"{coins_per_round}🪙 per correct answer!")
                message = await channel.send(embed=embed)
                await KumosLab.set.gameMessage(guild=ctx.guild, user=ctx.author, id=message.id)
                correct_countries = []
                countries = []
                random_country = await KumosLab.data.alldata()
                for i in random_country:
                    countries.append(i[0])
                while round != 10:
                    message = await KumosLab.get.gameMessage(guild=ctx.guild, user=ctx.author)
                    message = await ctx.fetch_message(message)
                    random_country = random.choice(countries)
                    countries.remove(random_country)
                    image = await KumosLab.data.flagdata(country=random_country)
                    countries = countries
                    answer_1 = random.choice(countries)
                    countries.remove(answer_1)
                    answer_2 = random.choice(countries)
                    countries.remove(answer_2)
                    answer_3 = random.choice(countries)
                    countries.remove(answer_3)

                    answers_array = [random_country, answer_1, answer_2, answer_3]
                    random.shuffle(answers_array)

                    # send the image
                    embed.title = f"`🌎` ROUND {round}/10"
                    embed.set_field_at(index=0, name="ANSWERS",
                                       value=f"```1️⃣ - {answers_array[0]}\n2️⃣ - {answers_array[1]}\n3️⃣ - {answers_array[2]}\n4️⃣ - {answers_array[3]}```")
                    embed.set_image(url=image)
                    embed.set_footer(text=f"{coins_per_round}🪙 per correct answer!")
                    await message.edit(embed=embed)

                    # send the embed
                    await message.add_reaction("1️⃣")
                    await message.add_reaction("2️⃣")
                    await message.add_reaction("3️⃣")
                    await message.add_reaction("4️⃣")

                    def check(reaction, user):
                        return user == ctx.author and str(reaction.emoji) in ['1️⃣', '2️⃣', '3️⃣', '4️⃣']

                    try:
                        reaction, user = await self.client.wait_for('reaction_add', timeout=120.0, check=check)
                    except asyncio.TimeoutError:
                        await message.delete()
                        emebed = discord.Embed(title="`🌎` TIME'S UP!", description="```You didn't answer in time!```")
                        emebed.add_field(name="ANSWER",
                                         value=f"```The correct answer was: {random_country}```")
                        emebed.set_image(url=image)
                        await channel.send(embed=emebed)
                        await KumosLab.add.ntflosses(user=ctx.author, amount=1, guild=ctx.guild)
                        embed = discord.Embed(title="`🌎` Play Again?", description="```Do you want to play again?```")
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
                                await self.gtf(ctx)
                            elif str(reaction.emoji) == "❌":
                                await channel.delete()
                                geo.delete_one(
                                    {'player_id': ctx.author.id, "guild": ctx.guild.id, "game_type": {"$exists": True}})
                                return

                    else:
                        if str(reaction.emoji) == '1️⃣':
                            if answers_array[0] == random_country:
                                round += 1
                                correct_countries.append(random_country)
                                await KumosLab.add.coins(guild=ctx.guild, user=ctx.author, amount=coins_per_round)
                                await message.remove_reaction(reaction.emoji, ctx.author)
                            else:
                                embed = discord.Embed(title="`🌎` YOU GOT THE WRONG ANSWER!")
                                embed.add_field(name="Correct answer", value=f"```{random_country}```")
                                embed.add_field(name="Round", value=f"```{round}```")
                                embed.add_field(name="Coins Earned",
                                                value=f"```{coins_per_round * len(correct_countries)}```", inline=False)
                                await KumosLab.add.ntflosses(guild=ctx.guild, user=ctx.author, amount=1)
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
                                        {'player_id': ctx.author.id, "guild": ctx.guild.id,
                                         "game_type": {"$exists": True}})
                                    return
                                else:
                                    if str(reaction.emoji) == "✅":
                                        await self.gtf(ctx)
                                    elif str(reaction.emoji) == "❌":
                                        await channel.delete()
                                        geo.delete_one(
                                            {'player_id': ctx.author.id, "guild": ctx.guild.id,
                                             "game_type": {"$exists": True}})
                                        return


                        elif str(reaction.emoji) == '2️⃣':
                            if answers_array[1] == random_country:
                                round += 1
                                correct_countries.append(random_country)
                                await KumosLab.add.coins(guild=ctx.guild, user=ctx.author,
                                                         amount=coins_per_round)
                                await message.remove_reaction(reaction.emoji, ctx.author)
                            else:
                                embed = discord.Embed(title="`🌎` YOU GOT THE WRONG ANSWER!")
                                embed.add_field(name="Correct answer", value=f"```{random_country}```")
                                embed.add_field(name="Round", value=f"```{round}```")
                                embed.add_field(name="Coins Earned",
                                                value=f"```{coins_per_round * len(correct_countries)}```", inline=False)
                                await KumosLab.add.ntflosses(guild=ctx.guild, user=ctx.author, amount=1)
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
                                        {'player_id': ctx.author.id, "guild": ctx.guild.id,
                                         "game_type": {"$exists": True}})
                                    return
                                else:
                                    if str(reaction.emoji) == "✅":
                                        await self.gtf(ctx)
                                    elif str(reaction.emoji) == "❌":
                                        await channel.delete()
                                        geo.delete_one(
                                            {'player_id': ctx.author.id, "guild": ctx.guild.id,
                                             "game_type": {"$exists": True}})
                                        return


                        elif str(reaction.emoji) == '3️⃣':
                            if answers_array[2] == random_country:
                                round += 1
                                correct_countries.append(random_country)
                                await KumosLab.add.coins(guild=ctx.guild, user=ctx.author,
                                                         amount=coins_per_round)
                                await message.remove_reaction(reaction.emoji, ctx.author)

                            else:
                                embed = discord.Embed(title="`🌎` YOU GOT THE WRONG ANSWER!")
                                embed.add_field(name="Correct answer", value=f"```{random_country}```")
                                embed.add_field(name="Round", value=f"```{round}```")
                                embed.add_field(name="Coins Earned",
                                                value=f"```{coins_per_round * len(correct_countries)}```", inline=False)
                                await channel.send(embed=embed)
                                await KumosLab.add.ntflosses(guild=ctx.guild, user=ctx.author, amount=1)
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
                                        {'player_id': ctx.author.id, "guild": ctx.guild.id,
                                         "game_type": {"$exists": True}})
                                    return
                                else:
                                    if str(reaction.emoji) == "✅":
                                        await self.gtf(ctx)
                                    elif str(reaction.emoji) == "❌":
                                        await channel.delete()
                                        geo.delete_one(
                                            {'player_id': ctx.author.id, "guild": ctx.guild.id,
                                             "game_type": {"$exists": True}})
                                        return


                        elif str(reaction.emoji) == '4️⃣':
                            if answers_array[3] == random_country:
                                round += 1
                                correct_countries.append(random_country)
                                await KumosLab.add.coins(guild=ctx.guild, user=ctx.author,
                                                         amount=coins_per_round)
                                await message.remove_reaction(reaction.emoji, ctx.author)

                            else:
                                embed = discord.Embed(title="`🌎` YOU GOT THE WRONG ANSWER!")
                                embed.add_field(name="Correct answer", value=f"```{random_country}```")
                                embed.add_field(name="Round", value=f"```{round}```")
                                embed.add_field(name="Coins Earned",
                                                value=f"```{coins_per_round * len(correct_countries)}```", inline=False)
                                await channel.send(embed=embed)
                                await KumosLab.add.ntflosses(guild=ctx.guild, user=ctx.author, amount=1)
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
                                        {'player_id': ctx.author.id, "guild": ctx.guild.id,
                                         "game_type": {"$exists": True}})
                                    return
                                else:
                                    if str(reaction.emoji) == "✅":
                                        await self.gtf(ctx)
                                    elif str(reaction.emoji) == "❌":
                                        await channel.delete()
                                        geo.delete_one(
                                            {'player_id': ctx.author.id, "guild": ctx.guild.id,
                                             "game_type": {"$exists": True}})
                                        return

                embed = discord.Embed(title=f"`🌎` YOU WON THE GAME! ROUND: `{round}`")
                embed.add_field(name="Correct answers",
                                value=f"```{str(correct_countries).replace('[', '').replace(']', '').replace('''''', '')}```")
                embed.add_field(name="Coins Earned",
                                value=f"```{coins_per_round * len(correct_countries) + coins_per_win}🪙```",
                                inline=False)
                await channel.send(embed=embed)
                await KumosLab.add.ntfwins(guild=ctx.guild, user=ctx.author, amount=1)
                await KumosLab.add.coins(guild=ctx.guild, user=ctx.author, amount=coins_per_win)
                embed = discord.Embed(title="`🌎` Play Again?", description="```Do you want to play again?```")
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
                        await self.gtf(ctx)
                    elif str(reaction.emoji) == "❌":
                        await channel.delete()
                        geo.delete_one(
                            {'player_id': ctx.author.id, "guild": ctx.guild.id, "game_type": {"$exists": True}})
                        return


def setup(client):
    client.add_cog(GuessTheFlag(client))
