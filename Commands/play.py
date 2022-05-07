import asyncio
import random

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


class Play(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, category):
        game_category = await KumosLab.get.gameCategory(guild=category.guild)
        if category.id == game_category:
            category = await category.guild.create_category(name="🎮 | GEO GAMES")
            geo.update_one({"guildid": category.guild.id, "bot_type": "GeoBot-Server"},
                           {"$set": {"category": category.id}})

    @commands.command(name='play', aliases=['p', 'pl', 'game'])
    async def play(self, ctx, *, gameName: str = None):
        db_search = geo.find_one({"Bot": True, "Maintenance": {"$exists": True}})
        if db_search["Maintenance"] is True:
            await ctx.reply("⚒️ The bot is currently under maintenance. The bot will return within **10** minutes.")
            return
        data_search = geo.find_one(
            {'player_id': ctx.author.id, "guild": ctx.guild.id, "game_type": {"$exists": True}})
        if data_search:
            await ctx.reply("**You already have a game in progress!**")
            return
        if gameName is None:
            await ctx.reply(f'**You need to specify a game name!**')
            return
        if gameName.lower() == 'gtf':
            await KumosLab.games.create(self=self, guild=ctx.guild, gameType=gameName.lower(), user=ctx.author)
        else:
            data_search = geo.find_one({'id': ctx.author.id, "guildid": ctx.guild.id, "bot_type": "GeoBot"})
            if data_search is None:
                await ctx.reply(f'**You have not been registered in the database!**')
                return
            if gameName.lower() in data_search['games_bought']:
                await KumosLab.games.create(self=self, guild=ctx.guild, gameType=gameName.lower(), user=ctx.author)
            else:
                await ctx.reply(f'**You do not have this game! Purchase it from the shop!**')
                return

    @commands.command(name='quit', aliases=['q'])
    async def quit(self, ctx):
        data_search = geo.find_one(
            {'player_id': ctx.author.id, "guild": ctx.guild.id, "game_type": {"$exists": True}})
        if data_search:
            channel = self.client.get_channel(data_search['channel_id'])
            geo.delete_one({'player_id': ctx.author.id, "guild": ctx.guild.id, "game_type": {"$exists": True}})
            await channel.delete()
        else:
            await ctx.reply("**You don't have a game in progress!**")
            return

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
                                value=f"```{coins_per_round * len(correct_countries) + coins_per_win}🪙```", inline=False)
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
                embed = discord.Embed(title=f"`🌎` HIGHER OR LOWER | {correct} CORRECT | 0 🪙", description="```Loading game...```")
                message = await channel.send(embed=embed)
            else:
                embed = discord.Embed(
                    title=f"`🌎` HIGHER OR LOWER | {correct} CORRECT | {coins_per_round * correct:,} 🪙", description="```Loading game...```")
                message = await channel.send(embed=embed)
            await message.add_reaction("⬆️")
            await message.add_reaction("⬇️")
            await KumosLab.set.gameMessage(guild=ctx.guild,user=ctx.author, id=message.id)
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
                    embed.description =f"`Which country is bigger?\n{last_country} | {country_2}`"
                    embed.add_field(name=f"{last_country}", value=f"```{country_1_size:,}km²```", inline=False)
                    embed.add_field(name=f"{country_2}", value=f"```    ⬆️       "
                                                               f"       OR       "
                                                               f"       ⬇️    ```", inline=True)
                else:
                    embed.title = f"`🌎` HIGHER OR LOWER | {correct} CORRECT | {coins_per_round * correct:,} 🪙"
                    embed.description =f"`Which country is bigger?\n{last_country} | {country_2}`"
                    embed.set_field_at(index=0, name=f"{last_country}", value=f"```{country_1_size:,}km²```", inline=False)
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


    @commands.command()
    async def gs(self, ctx):
        """
        Start a game of Guess the Size.
        :param ctx:
        :return:
        """
        data_search = geo.find_one(
            {'player_id': ctx.author.id, "guild": ctx.guild.id, "game_type": {"$exists": True}})

        if data_search:
            if data_search['game_type'] != "gs":
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
                coins_per_round = config['guess_shape_coins_per_win'] * 2
                await channel.send("`💸` **MULTIPLIER ACTIVATED! THIS ROUND HAS A MULTIPLIER OF x2 REWARDS!**")
            else:
                coins_per_round = config['guess_shape_coins_per_win']

            random_country = await KumosLab.data.allisocountries()
            countries = []
            for i in random_country:
                countries.append(i[0])
            random_country = random.choice(countries)
            iso = await KumosLab.data.getiso(country=random_country)

            image = await KumosLab.data.getcountryimage(country=random_country)

            embed = discord.Embed(title="`🌎` Guess the Shape!",
                                 description="```You have 6 Guesses to get the correct country!```")
            try:
                embed.set_image(url=image)
                await channel.send(embed=embed)
            except Exception as e:
                await channel.send(f"`💥` **There was an error starting your game - Please run {config['Prefix']}gs again. In compensation, you've been granted `300🪙's`**")
                await KumosLab.add.coins(guild=ctx.guild, user=ctx.author, amount=300)
                return

            guesses = 0
            while guesses < 6:
                member = data_search['player_id']
                member = await self.client.fetch_user(member)

                def check(m):
                    return m.author == member and m.channel == channel

                try:
                    message = await self.client.wait_for('message', check=check, timeout=300)
                except asyncio.TimeoutError:
                    embed = discord.Embed(title=f"`🌎` TIME IS UP! - {guesses}/6",
                                          description=f"The game has ended.")
                    embed.add_field(name=f"Correct Answer", value=f"```{random_country}```", inline=False)
                    embed.add_field(name="Coins Earned", value=f"```0🪙```")
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
                else:
                    if message.content.lower() == random_country.lower() or message.content.lower() == iso.lower() == iso.lower():
                        await message.add_reaction("✅")
                        best_score = await KumosLab.get.gsBestScore(guild=ctx.guild, user=ctx.author)
                        if guesses < best_score:
                            await KumosLab.set.gsBest(guild=ctx.guild, user=ctx.author, amount=guesses)
                        await KumosLab.add.gsWins(guild=ctx.guild, user=ctx.author, amount=1)
                        embed = discord.Embed(title=f"`🌎` YOU WIN! | {random_country} - {iso}")
                        embed.add_field(name="Coins Earned", value=f"```{coins_per_round:,}🪙```")
                        embed.add_field(name="Guesses To Win", value=f"```{guesses}```")
                        embed.set_image(url=image)
                        await channel.send(embed=embed)
                        await KumosLab.add.coins(guild=ctx.guild, user=ctx.author, amount=coins_per_round)
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
                                await self.gs(ctx)
                            elif str(reaction.emoji) == "❌":
                                await channel.delete()
                                geo.delete_one(
                                    {'player_id': ctx.author.id, "guild": ctx.guild.id, "game_type": {"$exists": True}})
                                return
                    else:
                        if guesses == 5:
                            await KumosLab.add.gsLosses(guild=ctx.guild, user=ctx.author, amount=1)
                            embed = discord.Embed(title="`🌎` YOU LOST! | 6/6 GUESSES")
                            embed.add_field(name="Correct Answer", value=f"```{random_country} - {iso}```")
                            embed.add_field(name="Coins Earned", value=f"`{0}🪙`")
                            embed.set_image(url=image)
                            await channel.send(embed=embed)

                            # ask if they want to play again
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
                                    await self.gs(ctx)
                                elif str(reaction.emoji) == "❌":
                                    await channel.delete()
                                    geo.delete_one(
                                        {'player_id': ctx.author.id, "guild": ctx.guild.id, "game_type": {"$exists": True}})
                                    return
                        else:
                            await message.add_reaction("❌")
                            guesses += 1


def setup(client):
    client.add_cog(Play(client))
