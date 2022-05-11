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
    async def play(self, ctx, gameName: str = None, publicity: str = None, *, key: str = None):
        db_search = geo.find_one({"Bot": True, "Maintenance": {"$exists": True}})
        if publicity is None:
            publicity = "public"
            if key is None:
                key = "public"
        if publicity.lower() == "private":
            if key is None:
                await ctx.reply("**You need to provide a password to host a private game!**")
                return
        if publicity.lower() == "public":
            if key is None:
                key = "public"
        key = key.lower().replace(" ", "_")
        if db_search["Maintenance"] is True:
            await ctx.reply("⚒️ The bot is currently under maintenance. The bot will return within **10** minutes.")
            return
        data_search = geo.find_one(
            {'player_id': ctx.author.id, "guild": ctx.guild.id, "game_type": {"$exists": True}})
        if data_search:
            await ctx.reply("**You already have a game in progress!**")
            return
        else:
            data_search = geo.find_one(
                {'host_id': ctx.author.id, "guild": ctx.guild.id, "game_type": {"$exists": True}})
            if data_search:
                await ctx.reply("**You already have a game in progress!**")
                return
        if gameName is None:
            await ctx.reply(f'**You need to specify a game name!**')
            return
        if gameName.lower() == 'gtf':
            await KumosLab.games.create(self=self, guild=ctx.guild, gameType=gameName.lower(), user=ctx.author, publicity=publicity.lower(), key=key.lower())
        else:
            data_search = geo.find_one({'id': ctx.author.id, "guildid": ctx.guild.id, "bot_type": "GeoBot"})
            if data_search is None:
                await ctx.reply(f'**You have not been registered in the database!**')
                return
            if gameName.lower() in data_search['games_bought']:
                await KumosLab.games.create(self=self, guild=ctx.guild, gameType=gameName.lower(), user=ctx.author, publicity=publicity.lower(), key=key.lower())
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
            data_search = geo.find_one(
                {'host_id': ctx.author.id, "guild": ctx.guild.id, "game_type": {"$exists": True}})
            if data_search:
                channel = self.client.get_channel(data_search['channel_id'])
                geo.delete_one({'host_id': ctx.author.id, "guild": ctx.guild.id, "game_type": {"$exists": True}})
                await channel.delete()
            else:
                await ctx.reply("**You don't have a game in progress!**")
                return

    @commands.command(name='join', aliases=['j'])
    async def join(self, ctx, user: discord.Member = None, *, key: str = None):
        if user is None:
            await ctx.reply("**You need to specify a user to join!**")
            return
        # check if game exists
        data_search = geo.find_one(
            {'host_id': user.id, "guild": ctx.guild.id, "game_type": {"$exists": True}})
        user_search = geo.find_one(
            {'host_id': ctx.author.id, "guild": ctx.guild.id, "game_type": {"$exists": True}})
        if user_search:
            await ctx.reply("**You already have a game in progress!**")
            return
        if data_search:
            # check if user is already in game
            game_search = geo.find(
                {"guild": ctx.guild.id, "players": {"$exists": True}})
            print(game_search)
            for x in game_search:
                print(x)
                print(x['players'])
                if ctx.author.id in x['players']:
                    await ctx.reply("**You are already in a game!**")
                    return
            if data_search['state'] == 'started':
                await ctx.reply("**That game has already started!**")
                return
            publicity = data_search['publicity']
            if publicity == 'public':
                if len(data_search['players']) >= 3:
                    await ctx.reply("**The game is full!**")
                    return
                # add user to game
                geo.update_one(
                    {'host_id': user.id, "guild": ctx.guild.id, "game_type": {"$exists": True}},
                    {'$push': {'players': ctx.author.id}}
                )
                channel = self.client.get_channel(data_search['channel_id'])
                # let the user see the channel
                await channel.set_permissions(ctx.author, read_messages=True, send_messages=True, read_message_history=True)
                # add 1 to the number of players
                geo.update_one(
                    {'host_id': user.id, "guild": ctx.guild.id, "game_type": {"$exists": True}},
                    {'$inc': {'player_count': 1}})
                player_count = data_search['player_count']
                await channel.send(f"➥ **{ctx.author.mention}** has joined the game! **{player_count + 1}/4**")
            elif publicity == 'private':
                if len(data_search['players']) >= 3:
                    await ctx.reply("**The game is full!**")
                    return
                if key is None:
                    await ctx.reply("**You must enter the games password to join!**")
                    return
                print(data_search['key'])
                print(key)
                if str(key).lower() == str(data_search['key']).lower():
                    # add user to game
                    geo.update_one(
                        {'host_id': user.id, "guild": ctx.guild.id, "game_type": {"$exists": True}},
                        {'$push': {'players': ctx.author.id}}
                    )
                    channel = self.client.get_channel(data_search['channel_id'])
                    await channel.set_permissions(ctx.author, read_messages=True, send_messages=True, read_message_history=True)
                    geo.update_one(
                        {'host_id': user.id, "guild": ctx.guild.id, "game_type": {"$exists": True}},
                        {'$inc': {'player_count': 1}})
                    player_count = data_search['player_count']
                    await channel.send(f"➥ **{ctx.author.mention}** has joined the game! **{player_count + 1}/4**")
                else:
                    await ctx.reply("**Invalid key!**")
                    return
            else:
                await ctx.reply("**That game is unobtainable at this moment.**")
        else:
            await ctx.reply("**That user has no game in progress!**")

    @commands.command(name="leave", aliases=["l"])
    async def leave(self, ctx):
        user_search = geo.find_one(
            {'host_id': ctx.author.id, "guild": ctx.guild.id, "game_type": {"$exists": True}})
        if user_search:
            await ctx.reply(f"**Please use {config['Prefix']}quit instead!**")
            return
        game_search = geo.find(
            {"guild": ctx.guild.id, "players": {"$exists": True}})
        for x in game_search:
            if ctx.author.id in x['players']:
                channel = self.client.get_channel(x['channel_id'])
                await channel.set_permissions(ctx.author, read_messages=False, send_messages=False, read_message_history=False)
                geo.update_one(
                    {'host_id': x['host_id'], "guild": ctx.guild.id, "game_type": {"$exists": True}},
                    {'$pull': {'players': ctx.author.id}}
                )
                # subtract 1 from the number of players
                geo.update_one(
                    {'host_id': x['host_id'], "guild": ctx.guild.id, "game_type": {"$exists": True}},
                    {'$inc': {'player_count': -1}}
                )
                player_count = x['player_count']
                await channel.send(f"➥ **{ctx.author.mention}** has left the game! **{player_count - 1}/4**")
                return
        await ctx.reply("**You are not in a game!**")

    @commands.command(name="invite", aliases=["inv", 'in'])
    async def invite(self, ctx, user: discord.Member = None):
        if user is None:
            await ctx.reply("**You must enter a user to invite!**")
            return
        if ctx.author.id == user.id:
            await ctx.reply("**You can't invite yourself!**")
            return
        member = user
        user_search = geo.find_one(
            {'host_id': ctx.author.id, "guild": ctx.guild.id, "game_type": {"$exists": True}})
        invited_user = geo.find_one(
            {'host_id': member.id, "guild": ctx.guild.id, "game_type": {"$exists": True}})
        if invited_user:
            await ctx.reply("**That user is already in a game!**")
            return
        in_game_check = geo.find(
            {'guild': ctx.guild.id})
        for x in in_game_check:
            if member.id in x['players']:
                await ctx.reply("**That user is already in a game!**")
                return
        if user_search:
            if user_search['player_count'] == 4:
                await ctx.reply("**The game is full!**")
                return
            channel = self.client.get_channel(user_search['channel_id'])
            await channel.send(f"➥ **{user.mention}** has been invited to join the game!")
            message = await user.send(f"➯ {ctx.author.mention} has invited you to a game!")
            await message.add_reaction("✅")
            await message.add_reaction("❌")
            def check(reaction, user):
                return user == member and reaction.message.id == message.id
            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout=30.0, check=check)
            except asyncio.TimeoutError:
                await message.delete()
                await ctx.reply(f"**The invite to {user.mention} has expired.**")
                return
            if str(reaction.emoji) == "✅":
                await message.edit(content=f"➯ **You have accepted the invite to {ctx.author.mention}'s game!**")
                geo.update_one(
                    {'host_id': ctx.author.id, "guild": ctx.guild.id, "game_type": {"$exists": True}},
                    {'$push': {'players': user.id}}
                )
                geo.update_one(
                    {'host_id': ctx.author.id, "guild": ctx.guild.id, "game_type": {"$exists": True}},
                    {'$inc': {'player_count': 1}}
                )
                await channel.set_permissions(user, read_messages=True, send_messages=True, read_message_history=True)
                player_count = user_search['player_count']
                await channel.send(f"➥ **{user.mention}** has joined the game! **{player_count + 1}/4**")
                return
            elif str(reaction.emoji) == "❌":
                await message.edit(content=f"➯ **You have declined the invite to {ctx.author.mention}'s game!**")
                player_count = user_search['player_count']
                await channel.send(f"➥ **{user.mention}** has declined the invite! **{player_count}/4**")
                return
        else:
            await ctx.reply("**You are not in a game!**")
            return









def setup(client):
    client.add_cog(Play(client))
