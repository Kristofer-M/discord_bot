import os
import random
import asyncio
import datetime
import re

import discord
from discord.ext import commands, tasks
from dateutil import parser

import dnd

# def AlarmTask():
#     def __init__(self, name):
#         self.name = name
#         self.task = alarm.start

die_regex = '[0-9]+d[0-9]+'

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
    if message.author == bot.user or str(message.author) != 'FallenRune#8591':
        return

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


@bot.command()
async def pun(context):
    await context.channel.send(random.choice(puns))


@bot.command()
async def hello(context):
    await context.channel.send("Hello!")


@bot.command()
async def alarm(context, day, time, *args):
    dt = datetime.datetime
    user_names = []
    alarm_name = []

    for arg in args:
        if str(arg).startswith('<@'):
            user_names.append(arg)
        else:
            alarm_name.append(arg)
    user_names = ' '.join(user_names)
    alarm_name = ' '.join(alarm_name)

    alarm = f'{day} {time}'
    await context.channel.send("Alarm set for {0}".format(str(alarm)))
    future_date = parser.parse(alarm)
    wait_time = future_date - dt.now()
    wait_time = wait_time.seconds
    alarm_tasks[alarm_name] = alarm_start.start(context, wait_time, alarm_name, user_names)


@tasks.loop(count=1)
async def alarm_start(context, wait_time, alarm_name, user_names):
    await asyncio.sleep(wait_time)
    alarm_tasks[alarm_name] = repeat_weekly.start(context, alarm_name, user_names)


@tasks.loop(seconds=2)
async def repeat_weekly(context, alarm_name, user_names):
    await context.channel.send(f'{alarm_name} {user_names}')


@bot.command()
async def stop(context):
    parsed_message_content = str(context.message.content).split()
    if len(parsed_message_content) < 2:
        await context.channel.send("More arguments required.")
        return
    else:
        alarm_name = " ".join(parsed_message_content[1:])
        alarm_tasks[alarm_name].cancel()
        await context.channel.send(f'{alarm_name} stopped.')


@bot.command()
async def stop_all(context):
    for alarm_name in alarm_tasks:
        alarm_tasks[alarm_name].cancel()
    await context.channel.send("All alarms stopped.")


@bot.command()
async def spell(context, *args):
    to_send = dnd.spell(args)
    try:
        await context.channel.send(to_send)
    except discord.errors.HTTPException:
        await context.channel.send(to_send[:1997] + '...')
        await context.channel.send('>>> ...' + to_send[1997:])


@bot.command()
async def test(context, *args):
    if re.match(die_regex, '2d8+3d6'):
        print('yeppers')


@bot.command()
async def roll(context, *args):
    result = dnd.roll(args)
    await context.channel.send(result)


if __name__ == '__main__':
    alarm_tasks = {}
    bot.run(os.getenv('DISCORD_BOT_TOKEN'))
