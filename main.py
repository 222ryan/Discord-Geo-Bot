import random
import re
from os import listdir
from discord.ext import commands, tasks
from discord.ext.commands import CommandNotFound, MemberNotFound
from ruamel.yaml import YAML
from ruamel.yaml import error
from dotenv import load_dotenv

import ruamel.yaml
import discord
import logging
import os
import warnings
import pyfiglet

if not os.path.isfile("Configs/config.yml"):
    print("[Error] Config file not found!")
    exit()

yaml = YAML()
with open("Configs/config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)

if config['Prefix'] is None:
    print("[Error] Prefix not found!")
    exit()
if config['OwnerID'] is None:
    print("[Error] OwnerID not found!")
    exit()

warnings.simplefilter('ignore', ruamel.yaml.error.UnsafeLoaderWarning)

client = commands.Bot(command_prefix=commands.when_mentioned_or(config['Prefix']), intents=discord.Intents.all(),
                      case_insensitive=True)
client.remove_command('help')

# Creating a file called logs.txt in the Logs folder, and then it is truncating it to 1 byte.
os.close(os.open("Logs/logs.txt", os.O_CREAT))
os.truncate("Logs/logs.txt", 1)
FORMAT = '[%(asctime)s]:[%(levelname)s]: %(message)s'
logging.basicConfig(filename='Logs/logs.txt', level=logging.DEBUG, format=FORMAT)
logging.debug('Begin Logging')
logging.info('Getting ready to login to Discord...')

# Checking if the .env file exists, if it doesn't, it will create it and ask you for your token, mongo_uri,
# collection_name, and database_name.
if not os.path.exists('.env'):
    print('[ERROR] .env file not found - Beginning setup...')
    token = input('Enter your Bot token: ')
    mongo_uri = input('Enter your MongoDB URI: ')
    collection_name = input('Enter your collection name: ')
    database_name = input('Enter your Database Collection name: ')
    weather_api_key = input('Enter your Weather API key (https://www.weatherapi.com/): ')

    with open('.env', 'w') as file:
        try:
            file.write('# Your Discord Bots Token -- Do not put in quotations and make sure you do not share this with '
                       'anyone!\n')
            file.write(f'DISCORD_TOKEN={token}\n\n')
            file.write('# This is the MongoDB Link you get after connecting your database to python. Make sure you '
                       'replace '
                       'your password and the database name!\n')
            file.write(f'MONGODB_URI={mongo_uri}\n\n')
            file.write('# These are the two entries for when you made a collection. For example, when i created mine, '
                       'i used discord and levelling, so for collection, mine would be "discord"\n# and for '
                       'database_name, mine would be "geobot" Note: This is based on what you entered! If you need '
                       'help with this, join the support server.\n')
            file.write(f'COLLECTION={collection_name}\n')
            file.write(f'DATABASE_NAME={database_name}\n')
            file.write("# https://www.weatherapi.com/ API Key -- Do not put in quotations and make sure you do not "
                       "share this with anyone else!\n# You can get a free API key by going to "
                       "https://www.weatherapi.com/")
            file.write(f'WEATHER_API={weather_api_key}\n')
            print('[SUCCESS] .env file created!')
        except Exception as e:
            print(f'[ERROR] There was an error creating the .env file. Please complete the setup manually with the '
                  f'following fields:\n- DISCORD_TOKEN\n- MONGODB_URI\n- COLLECTION\n- DATABASE_NAME\n- '
                  f'WEATHER_API\n\nThis is the '
                  f'result of this error: {e}')
            exit()

# Checking if the .env file has the correct variables in it. If it doesn't, it will exit the program.
load_dotenv()
if not os.environ.get('DISCORD_TOKEN'):
    print('[ERROR] DISCORD_TOKEN not found in .env file!')
    exit()
if not os.environ.get('MONGODB_URI'):
    print('[ERROR] MONGODB_URI not found in .env file!')
    exit()
if not os.environ.get('COLLECTION'):
    print('[ERROR] COLLECTION not found in .env file!')
    exit()
if not os.environ.get('DATABASE_NAME'):
    print('[ERROR] DATABASE_NAME not found in .env file!')
    exit()
if not os.environ.get('WEATHER_API'):
    print('[ERROR] WEATHER_API not found in .env file!')
    exit()

logging.info('Bot has passed all checks - Beginning login...')


@client.event
async def on_ready():
    """
    This function prints the ASCII banner, the invite link to the
    Discord server, the bots username and ID, and a few lines of text to make it look nice.
    """
    ascii_banner = pyfiglet.figlet_format("GEO-BOT")
    print(ascii_banner)
    print("Thank you for downloading Geo-Bot <3 \nIf you run into any issues, want to suggest a feature or "
          "want "
          "a place to hang out, join the Discord! discord.gg/UgvTHmuyNK\n")
    print("▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁")
    print('Logged In As:')
    print(f"Username: {client.user.name}\nID: {client.user.id}")
    print(f"Server Count: {len(client.guilds):,}")
    print(f"Members: {len(set(client.get_all_members())):,}")
    print(f"Commands: {len(client.commands):,}")
    print("▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁")
    await status_loop.start()


@tasks.loop(seconds=int(config['statusInterval']))
async def status_loop():
    if config['status'] is True:
        status_array = config['statusArray']
        # get a random status from the array
        status = str(random.choice(status_array)).replace(
            '@members', f'{len(set(client.get_all_members())):,}').replace('@guilds',
                                                                           f'{len(client.guilds):,}') \
            .replace(
            '@prefix', f'{config["Prefix"]} or @mention').replace('@commands', f'{len(client.commands):,}')
        if re.search(r'WATCHING', status, re.IGNORECASE):
            await client.change_presence(
                activity=discord.Activity(type=discord.ActivityType.watching, name=str(status).replace('WATCHING', '')))
        elif re.search(r'PLAYING', status, re.IGNORECASE):
            await client.change_presence(activity=discord.Game(name=str(status).replace('PLAYING', '')))
        elif re.search(r'LISTENING', status, re.IGNORECASE):
            await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening,
                                                                   name=str(status).replace('LISTENING', '')))
        else:
            await client.change_presence(activity=discord.Game(name="with @mention"))


@client.event
async def on_command_error(ctx, error):
    """
    If the command is not found, do nothing. If the member is not found, send an error message. If the error is not
    one of the above, raise the error

    :param ctx: The context of where the command was used
    :param error: The error that was raised
    :return: The error message.
    """
    if isinstance(error, CommandNotFound):
        return
    if isinstance(error, MemberNotFound):
        embed = discord.Embed(
            description=f"🔴 **ERROR**: `Member not found!`")
        await ctx.send(embed=embed)
        return
    raise error


# Loading all the commands and systems.
logging.info("------------- Loading -------------")
for fn in listdir("Commands"):
    if fn.endswith(".py"):
        logging.info(f"Loading: {fn}")
        client.load_extension(f"Commands.{fn[:-3]}")
        logging.info(f"Loaded {fn}")

for fn in listdir("System"):
    if fn.endswith(".py"):
        logging.info(f"Loading: {fn} System")
        client.load_extension(f"System.{fn[:-3]}")
        logging.info(f"Loaded {fn} System")
logging.info("------------- Finished Loading -------------")

# Getting the token from the .env file and then running the bot with that token.
token = os.getenv("DISCORD_TOKEN")
client.run(token)
