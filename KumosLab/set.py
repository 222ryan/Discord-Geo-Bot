import discord
from System.events import geo


async def gameData(guild: discord.Guild = None, user: discord.User = None, data: str = None):

    if guild is None:
        return "[get.gameCategory] Guild is None"
    if user is None:
        return "[get.gameCategory] User is None"
    if data is None:
        return "[get.gameCategory] Data is None"
    try:
        data_search = geo.find_one({"guild": guild.id, "game_type": {"$exists": True}, "player_id": user.id})
        # get category object
        if data_search is None:
            return None
        geo.update_one({"guild": guild.id, "game_type": {"$exists": True}, "player_id": user.id},
                       {"$set": {"data": data}})
    except Exception as e:
        return f"{e}"

async def gameMessage(guild: discord.Guild = None, user: discord.User = None, id: int = None):
    """
    Returns the message id of the game.
    :param guild:
    :param user:
    :param id:
    :return:
    """
    if guild is None:
        return "[add.gameMessage] Guild is None"
    if user is None:
        return "[add.gameMessage] User is None"
    if id is None:
        return "[add.gameMessage] ID is None"
    try:
        geo.update_one({"guild": guild.id, "game_type": {"$exists": True}, "player_id": user.id}, {"$set": {"message_id": id}})
    except Exception as e:
        return f"{e}"

async def holHighScore(guild: discord.Guild = None, user: discord.User = None, amount: int = None):
    """
    Returns the hol losses of the user.
    :param guild: The guild to get the hol losses from.
    :param user: The user to get the hol losses from.
    :param amount: The amount of hol losses to add.
    :return: The hol losses of the user.
    """
    if guild is None:
        return "[add.holLosses] Guild is None"
    if user is None:
        return "[add.holLosses] User is None"
    if amount is None:
        return "[add.holLosses] Amount is None"
    try:
        geo.update_one({"guildid": guild.id, "id": user.id, "bot_type": "GeoBot"}, {"$set": {"hol_highscore": amount}})
    except Exception as e:
        return f"{e}"

async def gsBest(guild: discord.Guild = None, user: discord.User = None, amount: int = None):
    """
    Returns the gs wins of the user.
    :param guild:
    :param user:
    :param amount:
    :return:
    """
    if guild is None:
        return "[add.gsWins] Guild is None"
    if user is None:
        return "[add.gsWins] User is None"
    if amount is None:
        return "[add.gsWins] Amount is None"
    try:
        geo.update_one({"guildid": guild.id, "id": user.id, "bot_type": "GeoBot"}, {"$set": {"gs_best": amount}})
    except Exception as e:
        return f"{e}"