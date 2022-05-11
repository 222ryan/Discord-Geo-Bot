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


class GuessShape(commands.Cog):
    def __init__(self, client):
        self.client = client

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
                await ctx.reply(
                    "⚒️ The bot is currently under maintenance. The bot will return within **10** minutes.")
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
                await channel.send(
                    f"`💥` **There was an error starting your game - Please run {config['Prefix']}gs again. In compensation, you've been granted `300🪙's`**")
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
                            await self.gs(ctx)
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
                                await self.gs(ctx)
                            elif str(reaction.emoji) == "❌":
                                await channel.delete()
                                geo.delete_one(
                                    {'player_id': ctx.author.id, "guild": ctx.guild.id,
                                     "game_type": {"$exists": True}})
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
                                    await self.gs(ctx)
                                elif str(reaction.emoji) == "❌":
                                    await channel.delete()
                                    geo.delete_one(
                                        {'player_id': ctx.author.id, "guild": ctx.guild.id,
                                         "game_type": {"$exists": True}})
                                    return
                        else:
                            await message.add_reaction("❌")
                            guesses += 1


def setup(client):
    client.add_cog(GuessShape(client))
