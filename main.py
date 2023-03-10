# This example requires the 'message_content' intent.
from dotenv import load_dotenv
load_dotenv()

import discord
import os
from discord.ext import commands
import logging

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

description = 'Smash Ranking Bot'
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='$', description=description, intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.command()
async def hello(ctx):
    await ctx.send('Hello!')

bot.run(os.environ.get('BOT_TOKEN'), log_handler=handler, log_level=logging.DEBUG)
