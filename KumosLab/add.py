import discord
from System.events import geo


async def coins(guild: discord.Guild = None, user: discord.User = None, amount: int = None):
    """
    Adds coins to the user.
    :param guild: The guild to get the coins from.
    :param user: The user to get the coins from.
    :param amount: The amount of coins to add.
    """
    if guild is None:
        return "[add.coins] Guild is None"
    if user is None:
        return "[add.coins] User is None"
    if amount is None:
        return "[add.coins] Amount is None"
    try:
        geo.update_one({"guildid": guild.id, "id": user.id, "bot_type": "GeoBot"}, {"$inc": {"coins": amount}})
    except Exception as e:
        return f"{e}"

async def ntfwins(guild: discord.Guild = None, user: discord.User = None, amount: int = None):
    """
    Returns the ntfw wins of the user.
    :param guild: The guild to get the ntfw wins from.
    :param user: The user to get the ntfw wins from.
    :param amount: The amount of ntfw wins to add.
    :return: The ntfw wins of the user.
    """
    if guild is None:
        return "[add.ntfwins] Guild is None"
    if user is None:
        return "[add.ntfwins] User is None"
    try:
        geo.update_one({"guildid": guild.id, "id": user.id, "bot_type": "GeoBot"}, {"$inc": {"ntf_wins": amount}})
    except Exception as e:
        return f"{e}"


async def ntflosses(guild: discord.Guild = None, user: discord.User = None, amount: int = None):
    """
    Returns the ntfw losses of the user.
    :param guild: The guild to get the ntfw losses from.
    :param user: The user to get the ntfw losses from.
    :return: The ntfw losses of the user.
    """
    if guild is None:
        return "[add.ntflosses] Guild is None"
    if user is None:
        return "[add.ntflosses] User is None"
    if amount is None:
        return "[add.ntflosses] Amount is None"
    try:
        geo.update_one({"guildid": guild.id, "id": user.id, "bot_type": "GeoBot"}, {"$inc": {"ntf_losses": amount}})
    except Exception as e:
        return f"{e}"

async def holWins(guild: discord.Guild = None, user: discord.User = None, amount: int = None):
    """
    Returns the hol wins of the user.
    :param guild: The guild to get the hol wins from.
    :param user: The user to get the hol wins from.
    :param amount: The amount of hol wins to add.
    :return: The hol wins of the user.
    """
    if guild is None:
        return "[add.holWins] Guild is None"
    if user is None:
        return "[add.holWins] User is None"
    if amount is None:
        return "[add.holWins] Amount is None"
    try:
        geo.update_one({"guildid": guild.id, "id": user.id, "bot_type": "GeoBot"}, {"$inc": {"hol_wins": amount}})
    except Exception as e:
        return f"{e}"

async def holLosses(guild: discord.Guild = None, user: discord.User = None, amount: int = None):
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
        geo.update_one({"guildid": guild.id, "id": user.id, "bot_type": "GeoBot"}, {"$inc": {"hol_losses": amount}})
    except Exception as e:
        return f"{e}"

async def holHighScore(guild: discord.Guild = None, user: discord.User = None, amount: int = None):
    """
    Returns the hol high score of the user.
    :param guild: The guild to get the hol high score from.
    :param user: The user to get the hol high score from.
    :param amount: The amount of hol high score to add.
    :return: The hol high score of the user.
    """
    if guild is None:
        return "[add.holHighScore] Guild is None"
    if user is None:
        return "[add.holHighScore] User is None"
    if amount is None:
        return "[add.holHighScore] Amount is None"
    try:
        geo.update_one({"guildid": guild.id, "id": user.id, "bot_type": "GeoBot"}, {"$inc": {"hol_highscore": amount}})
    except Exception as e:
        return f"{e}"

async def gsWins(guild: discord.Guild = None, user: discord.User = None, amount: int = None):
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
        geo.update_one({"guildid": guild.id, "id": user.id, "bot_type": "GeoBot"}, {"$inc": {"gs_wins": amount}})
    except Exception as e:
        return f"{e}"

async def gsLosses(guild: discord.Guild = None, user: discord.User = None, amount: int = None):
    """
    Returns the gs losses of the user.
    :param guild:
    :param user:
    :param amount:
    :return:
    """
    if guild is None:
        return "[add.gsLosses] Guild is None"
    if user is None:
        return "[add.gsLosses] User is None"
    if amount is None:
        return "[add.gsLosses] Amount is None"
    try:
        geo.update_one({"guildid": guild.id, "id": user.id, "bot_type": "GeoBot"}, {"$inc": {"gs_losses": amount}})
    except Exception as e:
        return f"{e}"



async def boughtGame(guild: discord.Guild = None, user: discord.User = None, game: str = None):
    """
    Adds a game to the user.
    :param guild: The guild to get the games from.
    :param user: The user to get the games from.
    :param game: The game to add.
    """
    if guild is None:
        return "[add.boughtGame] Guild is None"
    if user is None:
        return "[add.boughtGame] User is None"
    if game is None:
        return "[add.boughtGame] Game is None"
    try:
        geo.update_one({"guildid": guild.id, "id": user.id, "bot_type": "GeoBot"}, {"$push": {"games_bought": game}})
    except Exception as e:
        return f"{e}"

