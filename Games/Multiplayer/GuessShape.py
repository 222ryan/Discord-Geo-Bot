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


class GuessShapeM(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def gsm(self, ctx):
        """
        Start a game of Guess the Size.
        :param ctx:
        :return:
        """
        data_search = geo.find_one(
            {'host_id': ctx.author.id, "guild": ctx.guild.id, "game_type": {"$exists": True}})

        if data_search:
            if data_search['game_type'] != "gsm":
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
                    {'host_id': ctx.author.id, "guild": ctx.guild.id, "game_type": {"$exists": True}})
                return
            player_count = data_search['player_count']
            if player_count < 2:
                await channel.send("`🌎` **There are not enough players to start the game!**")
                return
            if channel.id == ctx.message.channel.id:
                embed = discord.Embed(title="`🌎` GET READY, THE GAME BEGINS IN 3 SECONDS!")
                messsage = await channel.send(embed=embed)
                await asyncio.sleep(3)
                await messsage.delete()
            multiplier_chance = random.randint(1, 100)
            if multiplier_chance >= 90:
                coins_per_round = config['guess_shape_coins_per_win'] * 2
                coins_for_participation = config['multiplayer_guess_shape_coins_per_participation'] * 2
                await channel.send("`💸` **MULTIPLIER ACTIVATED! THIS ROUND HAS A MULTIPLIER OF x2 REWARDS!**")
            else:
                coins_per_round = config['guess_shape_coins_per_win']
                coins_for_participation = config['multiplayer_guess_shape_coins_per_participation']

            random_country = await KumosLab.data.allisocountries()
            countries = []
            for i in random_country:
                countries.append(i[0])
            random_country = random.choice(countries)
            iso = await KumosLab.data.getiso(country=random_country)

            image = await KumosLab.data.getcountryimage(country=random_country)

            embed = discord.Embed(title="`🌎` Guess the Shape!",
                                  description="```Whoever guesses correctly first wins!```")
            embed.set_footer(text=f"Participation: {coins_for_participation} 🪙's | Winner {coins_per_round} 🪙's")
            try:
                embed.set_image(url=image)
                await channel.send(embed=embed)
            except Exception as e:
                await channel.send(
                    f"`💥` **There was an error starting your game - Please run {config['Prefix']}gsm again. In compensation, you've been granted `300🪙's`**")
                await KumosLab.add.coins(guild=ctx.guild, user=ctx.author, amount=300)
                return

            guesses = 0
            host = data_search['host_id']
            players = data_search['players']
            players.append(ctx.author.id)
            winner = []
            # set state to started
            geo.update_one(
                {'host_id': ctx.author.id, "guild": ctx.guild.id, "game_type": {"$exists": True}},
                {'$set': {'state': 'started'}})
            while len(winner) == 0:

                def check(m):
                    return m.author.id in players and m.channel == channel

                try:
                    message = await self.client.wait_for('message', check=check, timeout=300)
                except asyncio.TimeoutError:
                    embed = discord.Embed(title=f"`🌎` TIME IS UP!",
                                          description=f"```The correct answer was {random_country}```")

                    player_object = []
                    for player in players:
                        member = ctx.guild.get_member(player)
                        player_object.append(member.id)
                        await KumosLab.add.coins(guild=ctx.guild, user=member, amount=coins_for_participation)
                        await KumosLab.add.gsLosses(guild=ctx.guild, user=member, amount=1)

                    player_one = ctx.guild.get_member(player_object[0])
                    if player_count == 1:
                        player_two = "Player 2"
                        player_three = "Player 3"
                        player_four = "Player 4"
                    elif player_count == 2:
                        player_two = ctx.guild.get_member(player_object[1])
                        player_three = "Player 3"
                        player_four = "Player 4"
                    elif player_count == 3:
                        player_two = ctx.guild.get_member(player_object[1])
                        player_three = ctx.guild.get_member(player_object[2])
                        player_four = "Player 4"
                    else:
                        player_two = ctx.guild.get_member(player_object[1])
                        player_three = ctx.guild.get_member(player_object[2])
                        player_four = ctx.guild.get_member(player_object[3])

                    if player_one.id in winner:
                        player_one_coins_earned = coins_per_round + coins_for_participation
                        player_two_coins_earned = coins_for_participation
                        player_three_coins_earned = coins_for_participation
                        player_four_coins_earned = coins_for_participation
                    elif player_two.id in winner:
                        player_one_coins_earned = coins_for_participation
                        player_two_coins_earned = coins_per_round + coins_for_participation
                        player_three_coins_earned = coins_for_participation
                        player_four_coins_earned = coins_for_participation
                    else:
                        player_one_coins_earned = coins_for_participation
                        player_two_coins_earned = coins_for_participation
                        player_three_coins_earned = coins_for_participation
                        player_four_coins_earned = coins_for_participation
                    if player_count == 3:
                        if player_three.id in winner:
                            player_one_coins_earned = coins_for_participation
                            player_two_coins_earned = coins_for_participation
                            player_three_coins_earned = coins_per_round + coins_for_participation
                            player_four_coins_earned = coins_for_participation
                    elif player_count == 4:
                        if player_four.id in winner:
                            player_one_coins_earned = coins_for_participation
                            player_two_coins_earned = coins_for_participation
                            player_three_coins_earned = coins_for_participation
                            player_four_coins_earned = coins_per_round + coins_for_participation
                    else:
                        player_one_coins_earned = coins_for_participation
                        player_two_coins_earned = coins_for_participation
                        player_three_coins_earned = coins_for_participation
                        player_four_coins_earned = coins_for_participation

                    embed.add_field(name="Coins Earned",
                                    value=f"```{player_one} - {player_one_coins_earned}🪙\n{player_two} - {player_two_coins_earned}🪙\n{player_three} - {player_three_coins_earned}🪙\n{player_four} - {player_four_coins_earned}🪙```")

                    await channel.send(embed=embed)
                    embed = discord.Embed(title="`🌎` Play Again?",
                                          description="```Do you want to play again?```")
                    message = await channel.send(embed=embed)
                    await message.add_reaction("✅")
                    await message.add_reaction("❌")

                    geo.update_one(
                        {'host_id': ctx.author.id, "guild": ctx.guild.id, "game_type": {"$exists": True}},
                        {'$set': {'state': 'Waiting for Players..'}})

                    def check(reaction, user):
                        return user.id == host and reaction.message.id == message.id

                    try:
                        reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=30)
                    except asyncio.TimeoutError:
                        await channel.delete()
                        geo.delete_one(
                            {'host_id': ctx.author.id, "guild": ctx.guild.id, "game_type": {"$exists": True}})
                        return
                    else:
                        if str(reaction.emoji) == "✅":
                            await self.gsm(ctx)
                        elif str(reaction.emoji) == "❌":
                            await channel.delete()
                            geo.delete_one(
                                {'host_id': ctx.author.id, "guild": ctx.guild.id,
                                 "game_type": {"$exists": True}})
                            return
                else:
                    if message.content.lower() == random_country.lower() or message.content.lower() == iso.lower() == iso.lower():
                        await message.add_reaction("✅")
                        await KumosLab.add.gsWins(guild=ctx.guild, user=ctx.author, amount=1)
                        embed = discord.Embed(title=f"`🌎` {message.author} WINS! | {random_country} - {iso}")
                        winner.append(message.author.id)

                        player_object = []
                        for player in players:
                            member = ctx.guild.get_member(player)
                            player_object.append(member.id)
                            await KumosLab.add.coins(guild=ctx.guild, user=member, amount=coins_for_participation)
                            if player in winner:
                                await KumosLab.add.gsWins(guild=ctx.guild, user=member, amount=1)
                                await KumosLab.add.coins(guild=ctx.guild, user=member, amount=coins_per_round)
                            else:
                                await KumosLab.add.gsLosses(guild=ctx.guild, user=member, amount=1)

                        player_one = ctx.guild.get_member(player_object[0])
                        if player_count == 1:
                            player_two = "Player 2"
                            player_three = "Player 3"
                            player_four = "Player 4"
                        elif player_count == 2:
                            player_two = ctx.guild.get_member(player_object[1])
                            player_three = "Player 3"
                            player_four = "Player 4"
                        elif player_count == 3:
                            player_two = ctx.guild.get_member(player_object[1])
                            player_three = ctx.guild.get_member(player_object[2])
                            player_four = "Player 4"
                        else:
                            player_two = ctx.guild.get_member(player_object[1])
                            player_three = ctx.guild.get_member(player_object[2])
                            player_four = ctx.guild.get_member(player_object[3])

                        if player_one.id in winner:
                            player_one_coins_earned = coins_per_round + coins_for_participation
                            player_two_coins_earned = coins_for_participation
                            player_three_coins_earned = coins_for_participation
                            player_four_coins_earned = coins_for_participation
                        elif player_two.id in winner:
                            player_one_coins_earned = coins_for_participation
                            player_two_coins_earned = coins_per_round + coins_for_participation
                            player_three_coins_earned = coins_for_participation
                            player_four_coins_earned = coins_for_participation
                        elif player_three.id in winner:
                            player_one_coins_earned = coins_for_participation
                            player_two_coins_earned = coins_for_participation
                            player_three_coins_earned = coins_per_round + coins_for_participation
                            player_four_coins_earned = coins_for_participation
                        elif player_four.id in winner:
                            player_one_coins_earned = coins_for_participation
                            player_two_coins_earned = coins_for_participation
                            player_three_coins_earned = coins_for_participation
                            player_four_coins_earned = coins_per_round + coins_for_participation
                        else:
                            player_one_coins_earned = coins_for_participation
                            player_two_coins_earned = coins_for_participation
                            player_three_coins_earned = coins_for_participation
                            player_four_coins_earned = coins_for_participation

                        embed.add_field(name="Coins Earned", value=f"```{player_one} - {player_one_coins_earned}🪙\n{player_two} - {player_two_coins_earned}🪙\n{player_three} - {player_three_coins_earned}🪙\n{player_four} - {player_four_coins_earned}🪙```")
                        embed.set_image(url=image)
                        await channel.send(embed=embed)
                        await KumosLab.add.coins(guild=ctx.guild, user=ctx.author, amount=coins_per_round)
                        embed = discord.Embed(title="`🌎` Play Again?",
                                              description="```Do you want to play again?```")
                        message = await channel.send(embed=embed)
                        geo.update_one(
                            {'host_id': ctx.author.id, "guild": ctx.guild.id, "game_type": {"$exists": True}},
                            {'$set': {'state': 'Waiting for Players..'}})
                        await message.add_reaction("✅")
                        await message.add_reaction("❌")

                        def check(reaction, user):
                            return user.id == host and reaction.message.id == message.id

                        try:
                            reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=30)
                        except asyncio.TimeoutError:
                            await channel.delete()
                            geo.delete_one(
                                {'host_id': ctx.author.id, "guild": ctx.guild.id, "game_type": {"$exists": True}})
                            return
                        else:
                            if str(reaction.emoji) == "✅":
                                await self.gsm(ctx)
                            elif str(reaction.emoji) == "❌":
                                await channel.delete()
                                geo.delete_one(
                                    {'host_id': ctx.author.id, "guild": ctx.guild.id,
                                     "game_type": {"$exists": True}})
                                return
                    else:
                        await message.add_reaction("❌")


def setup(client):
    client.add_cog(GuessShapeM(client))
