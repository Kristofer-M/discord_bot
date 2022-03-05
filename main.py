import json
import os
import random
import asyncio
import datetime
import re
from math import log

import discord
from discord.ext import commands, tasks
from dateutil import parser
import dice
import simpleeval

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


# async def get_alarm_vars(context: commands.Context, day, time, args):
#     parsed_message_content = str(context.message.content).split()
#     if len(parsed_message_content) < 5:
#         await context.channel.send("More arguments required.")
#         return None
#
#     try:
#         index_day = days.index(day)
#
#         alarm_hour = time
#         hour = alarm_hour.split(":")[0]
#         minutes = alarm_hour.split(":")[1]
#         alarm_time = datetime.time(int(hour), int(minutes))
#
#         alarm = f'{day} {alarm_hour}'
#     except ValueError as v:
#         if 'list' in str(v):
#             v = str(v).split(" ")[0]
#             v += ' is not a day.'
#         await context.channel.send(v)
#         return None
#     except IndexError:
#         await context.channel.send("Please enter time in HH:MM format.")
#         return None
#
#     user_names = []
#     alarm_name = []
#     for arg in args:
#         if str(arg).startswith('<@'):
#             user_names.append(arg)
#         else:
#             alarm_name.append(arg)
#     user_names = ' '.join(user_names)
#     alarm_name = ' '.join(alarm_name)
#
#     return {
#         'user_names': user_names,
#         'alarm_name': alarm_name,
#         'alarm': alarm,
#         'alarm_time': alarm_time,
#         'day': index_day,
#     }


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
    spell_name = (' '.join(args)).lower()
    with open('dndspells.json', mode='r') as spell_file:
        spell_data = json.load(spell_file)
        spell = spell_data["spell"][spell_name]
        to_send = f'>>> {spell["name"]}\n' \
                  f'{spell["level"]} level {spell["school"]}\n' \
                  f'Casting time: {spell["time"]}\n' \
                  f'Range: {spell["range"]}\n' \
                  f'Components: {spell["components"].upper()}\n' \
                  f'Duration: {spell["duration"]}\n' \
                  f'{spell["desc"]}\n' \
                  f'{spell["upcast"]}'
        try:
            await context.channel.send(to_send)
        except discord.errors.HTTPException:
            await context.channel.send(to_send[:1997] + '...')
            await context.channel.send('>>> ...' + to_send[1997:])

@bot.command()
async def test(context, *args):
    if re.match(die_regex, '2d8+3d6'):
        print('yeppers')

def roll_adv(die):
    num_rolls = int(die[0])
    result = []
    for i in range(num_rolls):
        die_type = die.split('d')[1]
        dice_roll = list(dice.roll(f'2d{die_type}'))
        result.append((max(dice_roll)))
    return result


def find_spell_dice(spell_name):
    with open('dndspells.json', mode='r') as dnd_spells:
        try:
            spell_data = json.load(dnd_spells)
            spell = spell_data["spell"][spell_name]
            spell_dice = re.search(die_regex, spell['desc'])
            return spell_dice.group()
        except KeyError:
            pass


@bot.command()
async def roll(context, *args: str):
    args = list(args)

    for arg in args:
        if not re.match(die_regex, arg) or arg != 'adv':
            to_roll = find_spell_dice(arg)
            if to_roll is not None:
                index = args.index(arg)
                args[index] = to_roll

    expression = ''.join(args)
    dice_to_roll = re.findall(die_regex, expression)
    roll_result = []

    if 'adv' in args:
        expression = expression.replace('adv', '')
        for die in dice_to_roll:
            roll_result.append(list(roll_adv(die)))
    else:
        for die in dice_to_roll:
            roll_result.append(list(dice.roll(die)))

    for die, result in zip(dice_to_roll, roll_result):
        expression = expression.replace(die, str(sum(result)))

    total_result = simpleeval.simple_eval(expression, functions={'log': lambda x: log(x)})
    to_send = f'`{roll_result}` Result: {total_result}'
    await context.channel.send(to_send)


if __name__ == '__main__':
    alarm_tasks = {}
    bot.run(os.getenv('DISCORD_BOT_TOKEN'))
