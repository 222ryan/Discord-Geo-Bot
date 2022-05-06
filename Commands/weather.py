import os
import urllib.request, json

import discord
from discord.ext import commands
from dotenv import load_dotenv
import requests

load_dotenv()

class Weather(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name='weather', aliases=['w'])
    async def weather(self, ctx, *, city=None):
        """
        Get the weather in a city.
        """
        if city is None:
            embed = discord.Embed(description="`🔴` **Error**: `Please enter a valid location.`")
            await ctx.reply(embed=embed)
            return
        weather_api = os.environ.get('WEATHER_API')
        city = city.replace(' ', '%20')

        url = f"http://api.weatherapi.com/v1/current.json?key={weather_api}&q={city}&aqi=no"
        x = requests.get(f'http://api.weatherapi.com/v1/current.json?key={weather_api}&q={city}&aqi=no')
        if x.status_code == 400:
            embed = discord.Embed(description="`🔴` **Error**: `No matching location found.`")
            await ctx.reply(embed=embed)
            return
        if x.status_code == 401:
            embed = discord.Embed(description="`🔴` **Error**: `Invalid API key.`")
            await ctx.reply(embed=embed)
            return
        if x.status_code == 200:
            with urllib.request.urlopen(url) as url:
                    resp = json.loads(url.read().decode())
                    # get data
                    location = resp['location']['name']
                    region = resp['location']['region']
                    country = resp['location']['country']
                    time = resp['location']['localtime']

                    temperature = resp['current']['temp_c']
                    feelslike = resp['current']['feelslike_c']
                    humidity = resp['current']['humidity']
                    wind = resp['current']['wind_mph']
                    condition = resp['current']['condition']['text']
                    icon = resp['current']['condition']['icon']
                    pressure = resp['current']['pressure_mb']
                    cloudcover = resp['current']['cloud']
                    wind_dir = resp['current']['wind_dir']
                    uv = resp['current']['uv']

                    embed = discord.Embed(title=f"Weather in {location} - {condition}", description=f"```{location}, {region}, {country}\n{time}```")
                    embed.add_field(name="Current Conditions:", value=f"```- The temperature is {temperature}°C\n- Feels like {feelslike}°C"
                                                                      f"\n- {humidity}% Humidity\n- {wind}mph Wind Speeds\n- It is currently {condition}"
                                                                      f"\n- The pressure is {pressure}mb\n"
                                                                      f"- The sky is {cloudcover}% clouds\n- The wind "
                                                                      f"direction is {wind_dir}\n- The current UV "
                                                                      f"Index is {uv}```", inline=True)
                    embed.set_thumbnail(url=f"http:{icon}")
                    await ctx.reply(embed=embed)
def setup(client):
    client.add_cog(Weather(client))
