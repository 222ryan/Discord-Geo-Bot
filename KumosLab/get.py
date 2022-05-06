import discord
from System.events import geo


async def gameCategory(guild: discord.Guild = None):
    """
    Returns the category for the games.
    :param guild: The guild to get the category from.
    :return: The category for the games.
    """
    if guild is None:
        return "[get.gameCategory] Guild is None"
    try:
        data_search = geo.find_one({"guildid": guild.id, "bot_type": "GeoBot-Server"})
        # get category object
        if data_search is None:
            return None
    except Exception as e:
        return f"{e}"
    return data_search['category']

async def gameMessage(guild: discord.Guild = None, user: discord.User = None):
    """
    Returns the game message of the user.
    :param guild: The guild to get the game message from.
    :param user: The user to get the game message from.
    :return: The game message of the user.
    """
    if guild is None:
        return "[get.gameMessage] Guild is None"
    if user is None:
        return "[get.gameMessage] User is None"
    try:
        data_search = geo.find_one({"guild": guild.id, "player_id": user.id})
        # get category object
        if data_search is None:
            return None
    except Exception as e:
        return f"{e}"
    return data_search['message_id']

async def coins(guild: discord.Guild = None, user: discord.User = None):
    """
    Returns the coins of the user.
    :param guild: The guild to get the coins from.
    :param user: The user to get the coins from.
    :return: The coins of the user.
    """
    if guild is None:
        return "[get.coins] Guild is None"
    if user is None:
        return "[get.coins] User is None"
    try:
        data_search = geo.find_one({"guildid": guild.id, "id": user.id, "bot_type": "GeoBot"})
        # get category object
        if data_search is None:
            return None
    except Exception as e:
        return f"{e}"
    return data_search['coins']

async def ntfwins(guild: discord.Guild = None, user: discord.User = None):
    """
    Returns the ntfw wins of the user.
    :param guild: The guild to get the ntfw wins from.
    :param user: The user to get the ntfw wins from.
    :return: The ntfw wins of the user.
    """
    if guild is None:
        return "[get.ntfwins] Guild is None"
    if user is None:
        return "[get.ntfwins] User is None"
    try:
        data_search = geo.find_one({"guildid": guild.id, "id": user.id, "bot_type": "GeoBot"})
        # get category object
        if data_search is None:
            return None
    except Exception as e:
        return f"{e}"
    return data_search['ntf_wins']

async def ntflosses(guild: discord.Guild = None, user: discord.User = None):
    """
    Returns the ntfw losses of the user.
    :param guild: The guild to get the ntfw losses from.
    :param user: The user to get the ntfw losses from.
    :return: The ntfw losses of the user.
    """
    if guild is None:
        return "[get.ntflosses] Guild is None"
    if user is None:
        return "[get.ntflosses] User is None"
    try:
        data_search = geo.find_one({"guildid": guild.id, "id": user.id, "bot_type": "GeoBot"})
        # get category object
        if data_search is None:
            return None
    except Exception as e:
        return f"{e}"
    return data_search['ntf_losses']

async def holWins(guild: discord.Guild = None, user: discord.User = None):
    """
    Returns the hol wins of the user.
    :param guild: The guild to get the hol wins from.
    :param user: The user to get the hol wins from.
    :return: The hol wins of the user.
    """
    if guild is None:
        return "[get.holwins] Guild is None"
    if user is None:
        return "[get.holwins] User is None"
    try:
        data_search = geo.find_one({"guildid": guild.id, "id": user.id, "bot_type": "GeoBot"})
        # get category object
        if data_search is None:
            return None
    except Exception as e:
        return f"{e}"
    return data_search['hol_wins']

async def holLosses(guild: discord.Guild = None, user: discord.User = None):
    """
    Returns the hol losses of the user.
    :param guild: The guild to get the hol losses from.
    :param user: The user to get the hol losses from.
    :return: The hol losses of the user.
    """
    if guild is None:
        return "[get.hollosses] Guild is None"
    if user is None:
        return "[get.hollosses] User is None"
    try:
        data_search = geo.find_one({"guildid": guild.id, "id": user.id, "bot_type": "GeoBot"})
        # get category object
        if data_search is None:
            return None
    except Exception as e:
        return f"{e}"
    return data_search['hol_losses']

async def holHighScore(guild: discord.Guild = None, user: discord.User = None):
    """
    Returns the hol high score of the user.
    :param guild: The guild to get the hol high score from.
    :param user: The user to get the hol high score from.
    :return: The hol high score of the user.
    """
    if guild is None:
        return "[get.holhighscore] Guild is None"
    if user is None:
        return "[get.holhighscore] User is None"
    try:
        data_search = geo.find_one({"guildid": guild.id, "id": user.id, "bot_type": "GeoBot"})
        # get category object
        if data_search is None:
            return None
    except Exception as e:
        return f"{e}"
    return data_search['hol_highscore']

async def gsWins(guild: discord.Guild = None, user: discord.User = None):
    """
    Returns the gs wins of the user.
    :param guild: The guild to get the gs wins from.
    :param user: The user to get the gs wins from.
    :return: The gs wins of the user.
    """
    if guild is None:
        return "[get.gswins] Guild is None"
    if user is None:
        return "[get.gswins] User is None"
    try:
        data_search = geo.find_one({"guildid": guild.id, "id": user.id, "bot_type": "GeoBot"})
        if data_search is None:
            return None
    except Exception as e:
        return f"{e}"
    return data_search['gs_wins']

async def gsLosses(guild: discord.Guild = None, user: discord.User = None):
    """
    Returns the gs losses of the user.
    :param guild: The guild to get the gs losses from.
    :param user: The user to get the gs losses from.
    :return: The gs losses of the user.
    """
    if guild is None:
        return "[get.gslosses] Guild is None"
    if user is None:
        return "[get.gslosses] User is None"
    try:
        data_search = geo.find_one({"guildid": guild.id, "id": user.id, "bot_type": "GeoBot"})
        if data_search is None:
            return None
    except Exception as e:
        return f"{e}"
    return data_search['gs_losses']

async def gsBestScore(guild: discord.Guild = None, user: discord.User = None):
    """
    Returns the gs best score of the user.
    :param guild: The guild to get the gs best score from.
    :param user: The user to get the gs best score from.
    :return: The gs best score of the user.
    """
    if guild is None:
        return "[get.gsbestscore] Guild is None"
    if user is None:
        return "[get.gsbestscore] User is None"
    try:
        data_search = geo.find_one({"guildid": guild.id, "id": user.id, "bot_type": "GeoBot"})
        print(data_search)
        if data_search is None:
            return None
    except Exception as e:
        return f"{e}"
    return data_search['gs_best']


async def gameData(guild: discord.Guild = None, user: discord.User = None):
    """
    Returns the data of the user.
    :param guild: The guild to get the data from.
    :param user: The user to get the data from.
    :return: The data of the user.
    """
    if guild is None:
        return "[get.gameData] Guild is None"
    if user is None:
        return "[get.gameData] User is None"
    try:
        data_search = geo.find_one({"guild": guild.id, "game_type": {"$exists": True}, "player_id": user.id})
        # get category object
        if data_search is None:
            return None
    except Exception as e:
        return f"{e}"
    return data_search['data']