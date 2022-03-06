import json
import re
from math import log

import dice
from simpleeval import simple_eval

die_regex = '[0-9]+d[0-9]+'


def roll_adv(die):
    num_rolls = int(die[0])
    result = []
    for i in range(num_rolls):
        die_type = die.split('d')[1]
        dice_roll = list(dice.roll(f'2d{die_type}'))
        result.append((max(dice_roll)))
    return result


def find_spell_dice(spell_name, dnd_spells):
    try:
        spell_data = json.load(dnd_spells)
        spell = spell_data["spell"][spell_name]
        spell_dice = re.search(die_regex, spell['desc'])
        return spell_dice.group()
    except KeyError:
        pass


def roll(*args):
    args = [arg for tup in args for arg in tup]
    dnd_spells = open('dndspells.json')
    for arg in args:
        if not re.match(die_regex, arg) or arg != 'adv':
            to_roll = find_spell_dice(arg, dnd_spells)
            if to_roll is not None:
                index = args.index(arg)
                args[index] = to_roll
    dnd_spells.close()

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

    total_result = simple_eval(expression, functions={'log': lambda x: log(x)})
    to_send = f'`{roll_result}` Result: {total_result}'
    return to_send


def spell(*args):
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
    return to_send
