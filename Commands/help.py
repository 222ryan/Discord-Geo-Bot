import asyncio

import discord
from discord.ext import commands
from ruamel.yaml import YAML


yaml = YAML()
with open("Configs/config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)


class Help(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def help(self, ctx):
        try:
            prefix = config["Prefix"]
            if config['help_enabled'] is True:
                embed = discord.Embed(
                    title=f"{self.client.user.name}'s Command List")
                embed.set_thumbnail(url=self.client.user.avatar_url)
                embed.add_field(name="🎮 Games", value=f"`Game Commands`")
                embed.add_field(name="🌎 Fun", value=f"`Fun Commands`")
                embed.add_field(name="🛒 Shop", value=f"`Shopping Commands`")
                if ctx.author.id == int(config["OwnerID"]):
                    embed.add_field(name="🔧 Developer", value=f"`Developer Commands`")

                msg = await ctx.reply(embed=embed)
                await msg.add_reaction("🎮")
                await msg.add_reaction("🌎")
                await msg.add_reaction("🛒")
                if ctx.author.id == int(config["OwnerID"]):
                    await msg.add_reaction("🔧")


                def check(reaction, user):
                    return user == ctx.author and reaction.message.id == msg.id

                try:
                    reaction, user = await self.client.wait_for('reaction_add', timeout=60.0, check=check)
                    if reaction.emoji == "🎮":
                        # remove all reactions
                        await msg.clear_reactions()
                        embed = discord.Embed(title="🎮 Game Commands",
                                              description="```play, quit, leave, join, findmatch, invite```")
                        embed.add_field(name="Examples:",
                                        value=f"```🎮 {prefix}play <gameName> [<public|private>] [<key>]- Starts a game in your own custom channel\n"
                                              f"🎮 {prefix}quit - Deletes your game (Only works if you're the one who created it)\n"
                                              f"🎮 {prefix}leave - Leaves the game you're in (Only works if you're not the host)\n"
                                              f"🎮 {prefix}join <user> [<key>] - Joins another users multiplayer game\n"
                                              f"🎮 {prefix}findmatch <game> - Lets you find all public games by the game type you specified\n"
                                              f"🎮 {prefix}invite <user> - Invites a user to your game```")


                        await msg.edit(embed=embed)

                    elif reaction.emoji == "🌎":
                        # remove all reactions
                        await msg.clear_reactions()
                        embed = discord.Embed(title="🌎 Fun Commands", description="```weather, translate, stats, leaderboard```")
                        embed.add_field(name="Examples:", value=f"```🌤️ {prefix}weather <area> - Gives a detailed insight of the weather conditions in the specified area.\n"
                                                                f"💬 {prefix}translate <category> <channel> <area iso code> - Translated a message in the specified channel to the ISO language.\n"
                                                                f"💬 {prefix}stats [user] - Check yours or another users game stats.\n"
                                                                f"💬 {prefix}leaderboard [game] - Check the leaderboard for a specific game.```")
                        await msg.edit(embed=embed)
                    elif reaction.emoji == "🛒":
                        # remove all reactions
                        await msg.clear_reactions()
                        embed = discord.Embed(title="🛒 Shop Commands",
                                              description="```shop```")
                        embed.add_field(name="Examples:",
                                        value=f"```🛒 {prefix}shop [buy] [<item>] - Displays the shop or buys an item.```")
                        await msg.edit(embed=embed)
                    elif reaction.emoji == "🔧":
                        # remove all reactions
                        await msg.clear_reactions()
                        embed = discord.Embed(title="🔧 Maintenance Commands",
                                              description="```maintenance```")
                        embed.add_field(name="Examples:",
                                        value=f"```🔧 {prefix}maintenance - Enables maintenance mode. If you are planning on updating the bot, or going offline for a while, use this command. It prevents game creation and some other command to prevent issues in the future!```")
                        await msg.edit(embed=embed)

                except asyncio.TimeoutError:
                    await msg.delete()

        except Exception as e:
            print(f"[Help Command] {e}")


def setup(client):
    client.add_cog(Help(client))
