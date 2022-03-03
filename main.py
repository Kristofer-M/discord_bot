import os
import random
import asyncio
import datetime

import discord
from discord.ext import commands
from dateutil import parser

bot = commands.Bot(command_prefix='!')

seconds_in_week = 604800
seconds_in_day = 86400

days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
puns = [
    "What happened to the guy who sued over his missing luggage? He lost his case.",
    "How did you get hit on the head with a book? I only have my shelf to blame.",
    "What did one blade of grass say to another about the lack of rain? I guess we'll just have to make dew.",
    "I used to be addicted to soap, but I'm clean now."
]


@bot.event
async def on_ready():
    print("Logged in as {0}".format(bot.user))
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="ur mom lol"))


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if 'thanos' in str(message.content).lower():
        # loop.create_task(send_thanos(message))
        await send_thanos(message)

    elif '7 foot frame' in str(message.content).lower():
        await message.channel.send('https://tenor.com/view/encanto-camilo-madrigal-gif-24270871')

    elif 'everything is fine' in str(message.content).lower():
        await message.channel.send(
            'https://tenor.com/view/encanto-encanto-luisa-luisa-eye-luisa-eye-twitch-encanto-meme-gif-24306690')

    await bot.process_commands(message)



async def get_alarm_vars(context: commands.Context, day, time, args):
    parsed_message_content = str(context.message.content).split()
    if len(parsed_message_content) < 5:
        await context.channel.send("More arguments required.")
        return None

    try:
        index_day = days.index(day)

        alarm_hour = time
        hour = alarm_hour.split(":")[0]
        minutes = alarm_hour.split(":")[1]
        alarm_time = datetime.time(int(hour), int(minutes))

        alarm = f'{day} {alarm_hour}'
    except ValueError as v:
        if 'list' in str(v):
            v = str(v).split(" ")[0]
            v += ' is not a day.'
        await context.channel.send(v)
        return None
    except IndexError:
        await context.channel.send("Please enter time in HH:MM format.")
        return None

    user_names = []
    alarm_name = []
    for arg in args:
        if str(arg).startswith('<@'):
            user_names.append(arg)
        else:
            alarm_name.append(arg)
    user_names = ' '.join(user_names)
    alarm_name = ' '.join(alarm_name)

    return {
        'user_names': user_names,
        'alarm_name': alarm_name,
        'alarm': alarm,
        'alarm_time': alarm_time,
        'day': index_day,
    }


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
    future_date = parser.parse(alarm)
    await context.channel.send("Alarm set for {0}".format(str(alarm)))
    wait_time = future_date - dt.now()
    wait_time = wait_time.seconds

    await repeat_weekly(context, alarm_name, user_names, wait_time)


async def repeat_weekly(context, alarm_name, user_names, wait_time):
    while True:
        await asyncio.sleep(wait_time)
        await context.channel.send(f'{alarm_name} {user_names}')
        wait_time = seconds_in_week


# @bot.command()
# async def stop(context):
#     parsed_message_content = str(context.content).split()
#     if len(parsed_message_content) < 2:
#         await context.channel.send("More arguments required.")
#         return
#     else:
#         alarm_name = " ".join(parsed_message_content[1:])
#         alarm_tasks[alarm_name].cancel()
#         await context.channel.send(f'{alarm_name} stopped.')
#
#
# @bot.command()
# async def stop_all(context):
#     for alarm_name in alarm_tasks:
#         alarm_tasks[alarm_name].cancel()
#     await context.channel.send("All alarms stopped.")


if __name__ == '__main__':
    # alarm_tasks = {}
    # loop = asyncio.get_event_loop()
    bot.run(os.getenv('DISCORD_BOT_TOKEN'))
