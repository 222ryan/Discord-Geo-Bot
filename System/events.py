import os

from discord.ext import commands
from dotenv import load_dotenv
from pymongo import MongoClient
from ruamel.yaml import YAML

# It's loading the config.yml file and setting the variable config to the values in the config.yml file.

yaml = YAML()
with open("Configs/config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)

# Loading the .env file and setting the variables to the values in the .env file.
load_dotenv()
MONGODB_URI = os.environ['MONGODB_URI']
COLLECTION = os.getenv("COLLECTION")
DB_NAME = os.getenv("DATABASE_NAME")
cluster = MongoClient(MONGODB_URI)
geo = cluster[COLLECTION][DB_NAME]


# It's a class that inherits from the commands.Cog class, and it has a constructor that takes a client parameter
class Events(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.client.guilds:
            guild_search = geo.find_one({"guildid": guild.id, "bot_type": "GeoBot-Server"})
            if guild_search is None:
                # create a category
                category = await guild.create_category(name="🎮 | GEO GAMES")
                # add to database
                geo.insert_one(
                    {"guildid": guild.id, "bot_type": "GeoBot-Server", "category": category.id, "language": "en"})
            if str(config['data_register_type']).lower() == "on_startup":
                for member in guild.members:
                    if not member.bot:
                        search = geo.find_one(
                            {"id": member.id, "guildid": guild.id, "bot_type": "GeoBot"})
                        if search is None:
                            user_data = {"id": member.id, "bot_type": "GeoBot",
                                         "guildid": guild.id,
                                         "username": str(member), "ntf_wins": 0, "gs_wins": 0, "hol_wins": 0,
                                         "ntf_losses": 0, "gs_losses": 0, "hol_losses": 0, "games_bought": [],
                                         "coins": 100, "hol_highscore": 0, "gs_best": 6}
                            geo.insert_one(user_data)

    """
    If the user is not a bot, and the data register type is set to on_message, then check if the user is in the
    database, and if they're not, add them

    :param message: The message object
    """

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if config['data_register_type'].lower() == 'on_message':
            search = geo.find_one({"id": message.author.id, "guildid": message.author.guild.id, "bot_type": "GeoBot"})
            if search is None:
                user_data = {"id": message.author.id, "bot_type": "GeoBot", "guildid": message.author.guild.id,
                             "username": str(message.author), "ntf_wins": 0, "gs_wins": 0, "hol_wins": 0,
                             "ntf_losses": 0, "gs_losses": 0, "hol_losses": 0, "games_bought": [], "coins": 100, "hol_highscore": 0, "gs_best": 6}
                geo.insert_one(user_data)

    """
    When a guild is joined, if the guild is not in the database, add it to the database. If the guild is in the
    database, add all the members to the database.

    :param guild: The guild that the bot joined
    """

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        guild_search = geo.find_one({"guildid": guild.id, "bot_type": "GeoBot-Server"})
        if guild_search is None:
            # create a category
            category = await guild.create_category("🎮 | GEO GAMES")
            guild_data = {"guildid": guild.id, "bot_type": "GeoBot-Server", "language": "en",
                          "category": category.id}
            geo.insert_one(guild_data)
        for member in guild.members:
            if not member.bot:
                search = geo.find_one({"id": member.id, "guildid": guild.id, "bot_type": "GeoBot"})
                if search is None:
                    user_data = {"id": member.id, "bot_type": "GeoBot", "guildid": guild.id,
                                 "username": str(member), "ntf_wins": 0, "gs_wins": 0, "hol_wins": 0,
                                 "ntf_losses": 0, "gs_losses": 0, "hol_losses": 0, "games_bought": [], "coins": 100, "hol_highscore": 0, "gs_best": 6}
                    geo.insert_one(user_data)

    """
    It deletes all the data from the database that is associated with the guild that the bot has left

    :param guild: The guild that the bot was removed from
    """

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        geo.delete_many({"guildid": guild.id, "bot_type": "GeoBot"})
        geo.delete_many({"guildid": guild.id, "bot_type": "GeoBot-Server"})

    """
    If the user is not a bot, check if they're in the database. If they're not, add them

    :param member: The member that joined the server
    """

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not member.bot:
            search = geo.find_one({"id": member.id, "guildid": member.guild.id, "bot_type": "GeoBot"})
            if search is None:
                user_data = {"id": member.id, "bot_type": "GeoBot", "guildid": member.guild.id,
                             "username": str(member), "ntf_wins": 0, "gs_wins": 0, "hol_wins": 0,
                             "ntf_losses": 0, "gs_losses": 0, "hol_losses": 0, "games_bought": [], "coins": 100, "hol_highscore": 0, "gs_best": 6}
                geo.insert_one(user_data)

    """
    When a member leaves the server, the database is checked for the member's ID and the server's ID. If the member's ID
    and the server's ID are found, the member's data is deleted from the database

    :param member: The member that left the server
    """

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if not member.bot:
            geo.delete_one({"id": member.id, "guildid": member.guild.id, "bot_type": "GeoBot"})


def setup(client):
    """
    It adds the cog to the bot

    :param client: The bot object
    """
    client.add_cog(Events(client))
