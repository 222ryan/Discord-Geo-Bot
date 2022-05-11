import discord
from discord.ext import commands
from dotenv import load_dotenv
from ruamel.yaml import YAML

from System.events import geo
import KumosLab.games
import KumosLab.data
import KumosLab.get
import KumosLab.add

load_dotenv()
yaml = YAML()
with open("Configs/config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)


class Shop(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name='shop', aliases=['store'])
    async def shop(self, ctx, buy=None, *, item=None):
        db_search = geo.find_one({"Bot": True, "Maintenance": {"$exists": True}})
        if db_search["Maintenance"] is True:
            await ctx.reply("⚒️ The bot is currently under maintenance. The bot will return within **10** minutes.")
            return
        if buy is None:
            embed = discord.Embed(
                title="🛒 WELCOME TO THE SHOP",
                description=f"```Here you can buy Games with the 🪙's you've earned!\nBuy a game with {config['Prefix']}shop buy <game>\nYou have: {await KumosLab.get.coins(user=ctx.author, guild=ctx.guild):,} 🪙```")
            embed.add_field(name="↕️ - HOL (Higher Or Lower)", value=f"```Pick which countries area in km² is larger than the other country\nPrice: {config['higher_lower_price']:,} 🪙\nName: hol```", inline=False)
            embed.add_field(name="🟩 - GS (Guess Shape)", value=f"```Guess the countries name based on the shape of it\nPrice: {config['guess_shape_price']:,} 🪙\nName: gs```", inline=False)
            embed.add_field(name="🟩 - GSM (Guess Shape Multiplayer)", value=f"```Same as Guess Shape, but with Multiplayer!\nPrice: {config['multiplayer_guess_shape_price']:,} 🪙\nName: gsm```", inline=False)
            await ctx.send(embed=embed)

        elif buy.lower() == "buy":
            inventory_check = geo.find_one({"id": ctx.author.id, "guildid": ctx.guild.id, "bot_type": "GeoBot"})
            if item in inventory_check['games_bought']:
                embed = discord.Embed(
                    title="🛒 CHECKOUT FAILED",
                    description=f"```You already own this game!```")
                await ctx.send(embed=embed)
                return
            if item is None:
                embed = discord.Embed(
                    title="🛒 CHECKOUT FAILED",
                    description=f"```You didn't specify what you wanted to buy!```")
                await ctx.send(embed=embed)
                return
            elif item.lower() == "hol":
                if await KumosLab.get.coins(user=ctx.author, guild=ctx.guild) < config['higher_lower_price']:
                    embed = discord.Embed(
                        title="🛒 CHECKOUT FAILED",
                        description=f"```You don't have enough 🪙's to buy this game!```")
                    await ctx.send(embed=embed)
                    return
                else:
                    await KumosLab.add.coins(user=ctx.author, guild=ctx.guild, amount=-config['higher_lower_price'])
                    await KumosLab.add.boughtGame(user=ctx.author, guild=ctx.guild, game="hol")
                    embed = discord.Embed(
                        title="🛒 CHECKOUT SUCCESSFUL",
                        description=f"```You bought the game 'Higher Or Lower' for {config['higher_lower_price']:,} 🪙!```")
                    embed.add_field(name="New Balance", value=f"```{await KumosLab.get.coins(user=ctx.author, guild=ctx.guild):,} 🪙```")
                    await ctx.send(embed=embed)

            elif item.lower() == "gs":
                if await KumosLab.get.coins(user=ctx.author, guild=ctx.guild) < config['guess_shape_price']:
                    embed = discord.Embed(
                        title="🛒 CHECKOUT FAILED",
                        description=f"```You don't have enough 🪙's to buy this game!```")
                    await ctx.send(embed=embed)
                    return

                else:
                    await KumosLab.add.coins(user=ctx.author, guild=ctx.guild, amount=-config['guess_shape_price'])
                    await KumosLab.add.boughtGame(user=ctx.author, guild=ctx.guild, game="gs")
                    embed = discord.Embed(
                        title="🛒 CHECKOUT SUCCESSFUL",
                        description=f"```You bought the game 'Guess Shape' for {config['guess_shape_price']:,} 🪙!```")
                    embed.add_field(name="New Balance", value=f"```{await KumosLab.get.coins(user=ctx.author, guild=ctx.guild):,} 🪙```")
                    await ctx.send(embed=embed)
            elif item.lower() == "gsm":
                if await KumosLab.get.coins(user=ctx.author, guild=ctx.guild) < config['multiplayer_guess_shape_price']:
                    embed = discord.Embed(
                        title="🛒 CHECKOUT FAILED",
                        description=f"```You don't have enough 🪙's to buy this game!```")
                    await ctx.send(embed=embed)
                    return
                else:
                    await KumosLab.add.coins(user=ctx.author, guild=ctx.guild, amount=-config['multiplayer_guess_shape_price'])
                    await KumosLab.add.boughtGame(user=ctx.author, guild=ctx.guild, game="gsm")
                    embed = discord.Embed(
                        title="🛒 CHECKOUT SUCCESSFUL",
                        description=f"```You bought the game 'Guess Shape Multiplayer' for {config['multiplayer_guess_shape_price']:,} 🪙!```")
                    embed.add_field(name="New Balance", value=f"```{await KumosLab.get.coins(user=ctx.author, guild=ctx.guild):,} 🪙```")
                    await ctx.send(embed=embed)







def setup(client):
    client.add_cog(Shop(client))
