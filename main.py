import asyncio
import datetime
import os
import random
import pytz

import discord
from discord.ext import commands

import dnd, mta, vtm
import scheduling

# '<:madge:889181914236350484>' '<:bonk:819935649268105247>' 'HUNDmiau#3769'
emoji = None
target = 'HUNDmiau#3769'
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', activity=discord.Game(name="Under Construction"), intents=intents)
mydt = datetime.datetime.now().astimezone(pytz.timezone('Europe/Berlin'))

win = {
    'rock': 'scissors',
    'paper': 'rock',
    'scissors': 'paper'
}
lose = {
    'rock': 'paper',
    'scissors': 'rock',
    'paper': 'scissors'
}

emojis = {
    'rock': '✊',
    'paper': '✋',
    'scissors': '✌️'
}

puns = [
    "What happened to the guy who sued over his missing luggage? He lost his case.",
    "How did you get hit on the head with a book? I only have my shelf to blame.",
    "What did one blade of grass say to another about the lack of rain? I guess we'll just have to make dew.",
    "I used to be addicted to soap, but I'm clean now.",
    "A Human, Elf and Dragonborn walk into a bar, the Dwarf walks under it"
]


@bot.event
async def on_ready():
    print("Logged in as {0}".format(bot.user))


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if emoji is not None and target is not None and str(message.author) == target:
        await message.add_reaction(emoji)

    if 'thanos' in str(message.content).lower():
        await send_thanos(message)

    elif '7 foot frame' in str(message.content).lower():
        await message.channel.send('https://tenor.com/view/encanto-camilo-madrigal-gif-24270871')

    elif 'everything is fine' in str(message.content).lower():
        await message.channel.send(
            'https://tenor.com/view/encanto-encanto-luisa-luisa-eye-luisa-eye-twitch-encanto-meme-gif-24306690')

    await bot.process_commands(message)


async def send_thanos(message):
    with open('thanos_smile.jpg', 'rb') as fp:
        to_send = discord.File(fp, 'thanos.jpg')
        await message.channel.send(file=to_send)


async def send_message(context, text):
    await context.channel.send(text)


# MEME COMMANDS
@bot.command()
async def pun(context):
    await context.channel.send(random.choice(puns))


@bot.command()
async def hello(context):
    await context.channel.send("Hello!")


@bot.command()
async def madge(context):
    await context.message.add_reaction('<:madge:889181914236350484>')


# ALARM COMMANDS
@bot.command()
async def alarm(context, day, time, *args):
    await scheduling.alarm(context, day, time, args)


@bot.command()
async def stop(context, *args):
    args = [arg for arg in args]
    schedule_name = ' '.join(args)
    await scheduling.stop(context, schedule_name)


@bot.command()
async def stopall(context):
    await scheduling.stop_all(context)


# D&D COMMANDS
@bot.command()
async def oracle(context, *args):
    try:
        args = int(' '.join(args))
    except ValueError:
        args = 0
    to_send = dnd.oracle(args)
    await context.channel.send(to_send)


@bot.command()
async def keyword(context, *args):
    try:
        args = int(' '.join(args))
    except ValueError:
        args = 1
    to_send = dnd.keyword(args)
    await context.channel.send(to_send)


@bot.command()
async def generateNPC(context, location, number=1):
    if location.isnumeric():
        number = int(location)
        location = None
    to_send = dnd.generateNPC(location, number)
    await context.channel.send(to_send)


@bot.command()
async def spell(context, *args):
    args = ' '.join(args)
    to_send = dnd.spell(args)
    try:
        await context.channel.send(to_send)
    except discord.errors.HTTPException:
        await context.channel.send(to_send[:1997] + '...')
        await context.channel.send('>>> ...' + to_send[1997:])


@bot.command()
async def feat(context, *args):
    args = ' '.join(args)
    to_send = dnd.feat(args)
    try:
        await context.channel.send(to_send)
    except discord.errors.HTTPException:
        await context.channel.send(to_send[:1997] + '...')
        await context.channel.send('>>> ...' + to_send[1997:])


@bot.command()
async def roll(context, *args):
    args = ' '.join(args)
    result = dnd.roll(args)
    await context.channel.send(result)


@bot.command()
async def battle(context, target, *args):
    args = ' '.join(args)
    result = dnd.battle(target, args)
    await context.channel.send(result)


@bot.command()
async def rollv(context, number, hunger=None, target=None):
    result = vtm.rollv(number, hunger, target)
    await context.channel.send(result)


@bot.command()
async def rerollv(context: discord.ext.commands.Context, number, hunger=None, target=None):
    c_history = context.channel.history(limit=10)
    result = "No roll message found."
    async for message in c_history:
        if str(message.author) == "Wizard's Assistant#0029":
            if 'Roll' in str(message.content):
                result = vtm.rerollv(str(message.content), number, hunger, target)
                break
    await context.channel.send(result)


# MAGE: THE ASCENSION COMMANDS
@bot.command()
async def rollm(context, number, success_criteria):
    number = int(number)
    success_criteria = int(success_criteria)
    result = mta.rollm(number, success_criteria)
    await context.channel.send(result)


@rollm.error
async def rollm_error(context, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await context.channel.send('To use the command, type:\n`!rollm [number of rolls] [difficulty class]`')


# MISCELLANEOUS COMMANDS
@bot.command()
async def exec(context, *args):
    if str(context.message.author) != 'FallenRune#8591':
        return
    args = list(args)
    args = " ".join(args)
    await eval(args)


@bot.command()
async def write(context, *text):
    text = ' '.join(text)
    text = text.replace('"', '\\"')
    text_str = text[0]
    message = await context.send(text_str)
    text = text[1:]

    for letter in text:
        text_str += letter
        await asyncio.sleep(0.2)
        await message.edit(content=text_str)


@bot.command()
async def game(context, choice):
    to_send = '>>> '
    if choice.lower() not in ['rock', 'paper', 'scissors']:
        await context.send('Enter a valid option.')
        return

    to_send += f'You picked {emojis[choice.lower()]}\n'
    # await context.send()

    outcome = random.choice(["You won", "You lost", "You drew"])
    bot_pick = ''
    if outcome == 'You won':
        to_send += f'Bot picks {emojis[win[choice]]}\n'
        # await context.send()
        bot_pick = emojis[win[choice]]
    elif outcome == 'You lost':
        to_send += f'Bot picks {emojis[lose[choice]]}\n'
        # await context.send()
        bot_pick = emojis[lose[choice]]
    else:
        to_send += f'Bot picks {emojis[choice.lower()]}\n'
        bot_pick = emojis[choice.lower()]

    to_send += f'{emojis[choice.lower()]} vs {bot_pick}\n'
    to_send += outcome
    await context.send(to_send)


@bot.command()
async def timecode(context, hour, minute,
                   day=mydt.now().day,
                   month=mydt.now().month,
                   year=mydt.now().year):
    result = scheduling.timecode(year, month, day, hour, minute)
    await context.send(result)


async def set_target(new_target):
    global target
    target = new_target


async def set_emoji(new_emoji):
    global emojis
    emojis = new_emoji


if __name__ == '__main__':
    token = os.getenv('DISCORD_TOKEN')
    bot.run(token)
