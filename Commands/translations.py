import asyncio

import discord
from discord.ext import commands
from dotenv import load_dotenv
from googletrans import Translator

from System.events import geo

load_dotenv()


class Translations(commands.Cog):
    def __init__(self, client):
        self.client = client

    """
    It translates a message from a channel to a language of your choice

    :param ctx: The context of the command
    :param channel: discord.TextChannel = None
    :type channel: discord.TextChannel
    :param message: discord.Message = None
    :type message: int
    :param language: The language you want to translate to, defaults to en
    :return: A discord.Embed object
    """

    @commands.command(name='translate', aliases=['tr'])
    async def translate(self, ctx, channel: discord.TextChannel = None, message: int = None, language='en'):
        db_search = geo.find_one({"Bot": True, "Maintenance": {"$exists": True}})
        if db_search["Maintenance"] is True:
            await ctx.reply("⚒️ The bot is currently under maintenance. The bot will return within **10** minutes.")
            await asyncio.sleep(10)
            await channel.delete()
            geo.delete_one(
                {'player_id': ctx.author.id, "guild": ctx.guild.id, "game_type": {"$exists": True}})
            return
        if channel is None:
            embed = discord.Embed(description="`🔴` **Error**: `Please enter a valid channel`")
            await ctx.reply(embed=embed)
            return
        if message is None:
            embed = discord.Embed(description="`🔴` **Error**: `Please enter a valid message id`")
            await ctx.reply(embed=embed)
            return
        try:
            message = await channel.fetch_message(message)
        except discord.NotFound:
            embed = discord.Embed(description="`🔴` **Error**: `Message not found`")
            await ctx.reply(embed=embed)
            return
        try:
            moment_message = await ctx.reply(f"`💬` **Translating**! This may take a moment...")
            translator = Translator()
            translated = translator.translate(message.content, dest=language)
            embed = discord.Embed(
                title=f"Translated from {str(translated.src).upper()} to {str(translated.dest).upper()}")
            embed.add_field(name="Original", value=f"```{message.content}```")
            embed.add_field(name="Translated", value=f"```{translated.text}```")
            await moment_message.edit(content="`💬` **Translated**!", embed=embed)
        except Exception as e:
            embed = discord.Embed(title="Click For ISO Codes", url="https://www.iban.com/country-codes", description="`🔴` **Error**: `There was an error translating the message! Ensure "
                                              "you entered a valid ISO Alpha-2 language code!`")
            await ctx.reply(embed=embed)


def setup(client):
    client.add_cog(Translations(client))
