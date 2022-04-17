import asyncio
import os
import random

import discord
from discord.ext import commands

import dnd
import scheduling

emoji = '<:madge:889181914236350484>'
target = 'seiarc#7644'
bot = commands.Bot(command_prefix='!', activity=discord.Game(name="Under Construction"))

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

    if str(message.author) == target:
        await message.add_reaction('emoji')

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


@bot.command()
async def pun(context):
    await context.channel.send(random.choice(puns))


@bot.command()
async def hello(context):
    await context.channel.send("Hello!")


@bot.command()
async def madge(context):
    await context.message.add_reaction('<:madge:889181914236350484>')


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
async def roll(context, *args):
    args = ' '.join(args)
    result = dnd.roll(args)
    await context.channel.send(result)

@bot.command()
async def rollv(context, number, hunger=None, target=None):
    result = dnd.rollv(number, hunger, target)
    await context.channel.send(result)

@bot.command()
async def test(context, *args):
    pass


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


async def set_target(new_target):
    global target
    target = new_target


async def set_emoji(new_emoji):
    global emoji
    emoji = new_emoji


if __name__ == '__main__':
    bot.run(os.getenv('DISCORD_BOT_TOKEN'))
