import json
import random
import re
from math import log

import dice
from simpleeval import simple_eval

# allowed_expressions = [
#     '+',
#     '**',
#     '(',
#     ')',
#     '*',
#     '/',
#     '-'
# ]
oracle_results = {}

for number in range(-7, 29):
    if number <= 2:
        oracle_results[number] = 'No, and'
    elif number <= 7:
        oracle_results[number] = 'No'
    elif number <= 9:
        oracle_results[number] = 'No, but'
    elif number == 10:
        oracle_results[number] = 'Maybe'
    elif number <= 12:
        oracle_results[number] = 'Yes, but'
    elif number <= 18:
        oracle_results[number] = 'Yes'
    else:
        oracle_results[number] = 'Yes, and'

keywords = {}
with open('keywords.txt', 'r') as f:
    for line in f.readlines():
        try:
            parsed_line = line.split('. ')
            keywords[int(parsed_line[0])] = parsed_line[1]
        except:
            print(line)
            raise IndexError

die_regex = '[0-9]+d[0-9]+'
word_regex = f'[^\d\W]+'


def roll_adv(die):
    num_rolls = int(die[0])
    result = []
    for i in range(num_rolls):
        die_type = die.split('d')[1]
        dice_roll = list(dice.roll(f'2d{die_type}'))
        result.append((max(dice_roll)))
    return result


def find_spell_dice(spell_name, spell_data):
    try:
        spell = spell_data["spell"][spell_name]
    except KeyError:
        spell_name = find_feature(spell_name, spell_data, 'spell')
        if spell_name is None:
            return None
        spell = spell_data['spell'][spell_name]

    spell_dice = re.search(die_regex, spell['desc'])
    return spell_dice.group()
    # except KeyError:
    #     return None
    # except AttributeError:
    #     # if spell_name not in allowed_expressions:
    #     #     main.send_message(f'{spell_name} either doesn\'t exist or I wasn\'t able to find dice to roll for it.')
    #     return None


def roll(expression):
    # args = [arg for tup in args for arg in tup]
    expression = replace_spell_dice(expression)

    # expression = ''.join(expression)
    dice_to_roll = re.findall(die_regex, expression)
    roll_result = []

    if 'adv' in expression:
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


def battle(target, expression):
    target = int(target)
    count = 0
    dice_rolled = dice.roll(expression)
    for number in dice_rolled:
        if number >= target:
            count += 1
    return count


def replace_spell_dice(expression):
    dnd_spells = open('dndspells.json')
    spell_data = json.load(dnd_spells)
    temp = re.findall(word_regex, expression)
    try:
        spells = [i for i in temp if i != 'd']
    except ValueError:
        pass
    for spell in spells:
        die = find_spell_dice(spell, spell_data)
        if die is None:
            continue
        expression = expression.replace(spell, die)
    dnd_spells.close()
    return expression


def find_feature(feature_name, feature_data, type):
    for data_item in feature_data[type].keys():
        if feature_name in data_item:
            return data_item
    return None


def spell(spell_name):
    spell_name = spell_name.lower()
    with open('dndspells.json', mode='r') as spell_file:
        spell_data = json.load(spell_file)
        try:
            spell = spell_data["spell"][spell_name]
        except KeyError:
            temp = find_feature(spell_name, spell_data, 'spell')
            if temp is None:
                return f'{spell_name} not found.'
            spell_name = temp
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

def feat(feat_name: str):
    feat_name = feat_name.lower()
    with open('dndfeats.json') as feat_file:
        feat_data = json.load(feat_file)
        try:
            feat = feat_data["feat"][feat_name]
        except KeyError:
            temp = find_feature(feat_name, feat_data, 'spell')
            if temp is None:
                return f'{feat_name} not found.'
            feat_name = temp
            feat = feat_data["spell"][feat_name]

    to_send = f'>>> {feat["name"]}\n' \
              f'{feat["desc"]}'
    return to_send


def oracle(possibility=0):
    result = int(dice.roll('1d20'))
    result += possibility
    print(result)
    return oracle_results[result]


def keyword(num: int):
    to_send = '>>> '
    for i in range(num):
        result = int(dice.roll('1d798'))
        to_send += keywords[result]
    return to_send


if __name__ == '__main__':
    print(keyword(3))
