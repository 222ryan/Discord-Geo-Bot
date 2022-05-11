import datetime

import discord
from ruamel.yaml import YAML

import KumosLab.get
import KumosLab.get
from System.events import geo

yaml = YAML()
with open("Configs/config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)



async def create(self, guild: discord.Guild = None, user: discord.Member = None, gameType: str = None, publicity: str = None, key: str = None):
    """
    Creates a new game.
    :param guild: The guild the game is being created in.
    :param user: The user who created the game.
    :param gameType: The type of game being created.
    :return: The game object.
    """
    if guild is None:
        return "[game.create] Guild is None."
    if user is None:
        return "[game.create] User is None."
    if gameType is None:
        return "[game.create] Game type is None."
    if publicity is None:
        return "[game.create] Publicity is None."

    if publicity == "public":
        key = "public"
    elif publicity == "private":
        if key is None:
            return

    category_id = await KumosLab.get.gameCategory(guild=guild)
    category = discord.utils.get(guild.categories, id=int(category_id))
    channel = await guild.create_text_channel(name=f"🌐 {user} {gameType}", category=category)
    # allow the bot to see the channel
    await channel.set_permissions(self.client.user, read_messages=True, send_messages=True, read_message_history=True)
    await channel.set_permissions(user, read_messages=True, send_messages=True, read_message_history=True)
    await channel.set_permissions(guild.default_role, read_messages=False, send_messages=False, read_message_history=False)
    await channel.send(f"{user.mention},")
    if gameType.lower() == "gtf":
        embed = discord.Embed(title="🏳️ Welcome To **Guess The Flag**!")
        embed.add_field(name="🎮 How To Play?", value="```You will be given an image of a flag, you must select the "
                                                   "option that you believe is the correct answer.```", inline=False)
        embed.add_field(name="🏆 How To Win?", value="```You must answer 10 questions in a row to win.```", inline=False)
        embed.add_field(name="▶️ How To Start?", value="```You can start the game by typing !gtf in this channel.```", inline=False)
        await channel.send(embed=embed)
        type = "Singleplayer"
    elif gameType.lower() == "hol":
        embed = discord.Embed(title="↕️ Welcome To **Higher Or Lower**!")
        embed.add_field(name="🎮 How To Play?", value="```You will be given 2 random countries with it's area size in "
                                                   "km². "
                                                   "You will have to declare whether one of which is higher or "
                                                   "lower.```", inline=False)
        embed.add_field(name="🏆 How To Win?", value="```You must answer a question correctly```", inline=False)
        embed.add_field(name="▶️ How To Start?", value="```You can start the game by typing !hol in this channel.```", inline=False)
        await channel.send(embed=embed)
        type = "Singleplayer"
    elif gameType.lower() == "gs":
        embed = discord.Embed(title="🏳️ Welcome To **Guess The Shape**!", description="For a list of country ISO codes, click [here](https://www.iban.com/country-codes).")
        embed.add_field(name="🎮 How To Play?", value="```You will be given an image of a random countries outline and you must guess the countries name.``` ")
        embed.add_field(name="🏆 How To Win?", value="```Guess the correct answer by typing the name of it within 6 guesses. You may also use ISO codes, which can be found in the description of this embed. Use Alpha-2 Codes.```", inline=False)
        embed.add_field(name="▶️ How To Start?", value="```You can start the game by typing !gs in this channel.```", inline=False)
        await channel.send(embed=embed)
        type = "Singleplayer"
    elif gameType.lower() == "gsm":
        embed = discord.Embed(title=f"🏳️ Welcome To **Guess The Shape MULTIPLAYER**!", description="For a list of country ISO codes, click [here](https://www.iban.com/country-codes).")
        embed.add_field(name="🔑 Game Code?", value=f"```If the game is private, members can use {config['Prefix']}join {user.id} {key.lower().replace(' ', '_')} to join this game!``` ")
        embed.add_field(name="🎮 How To Play?", value="```You will be given an image of a random countries outline and you must guess the countries name.``` ")
        embed.add_field(name="🏆 How To Win?", value="```Whoever guesses the correct answer first wins. You may also use ISO codes, which can be found in the description of this embed. Use Alpha-2 Codes.```", inline=False)
        embed.add_field(name="▶️ How To Start?", value="```The host can start the game by typing !gsm in this channel.```", inline=False)
        await channel.send(embed=embed)
        await channel.send("`🌎` **Waiting for at least 1 more player to join the game!**")
        type = "Multiplayer"
    else:
        type = "Singleplayer"
        return

    if type == "Singleplayer":
        game_data = {
            "guild": guild.id,
            "player_id": user.id,
            "game_type": gameType,
            "channel_id": channel.id,
            "created_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data": None,
            "message_id": None
        }
        geo.insert_one(game_data)
    else:
        game_data = {
            "guild": guild.id,
            "host_id": user.id,
            "game_type": gameType,
            "channel_id": channel.id,
            "created_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data": None,
            "message_id": None,
            "players": [],
            "player_count": 1,
            "publicity": publicity,
            "key": key,
            "state": "Waiting for Players.."
        }
        geo.insert_one(game_data)


