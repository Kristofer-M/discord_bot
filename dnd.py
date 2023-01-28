import json
import random
import re
from math import log
import numpy

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

races = None
with open('races.json', 'r') as f:
    races = json.load(f)
default_location = None

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

keywords = []
with open('keywords_new.txt', 'r') as f:
    for line in f.readlines():
        line = line.replace('\n', '')
        keywords.append(line)

professions = []
with open('professions.txt', 'r') as f:
    for line in f.readlines():
        professions.append(line.replace('\n', ''))

alignments = []
for ge in ['Good', 'Neutral', 'Evil']:
    for lc in ['Lawful', 'Neutral', 'Chaotic']:
        if ge == lc:
            alignments.append('True Neutral')
        else:
            alignments.append(f'{lc} {ge}')

p_alignments = [15, 20, 25, 30, 50, 55, 70, 90, 100]

employ = ['Commoner', 'Professional', 'Adventurer']
employ_cum = [25, 90, 100]

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
    result = '>>> '
    for i in range(num):
        result += random.choice(keywords) + '\n'
    return result


""" RACES:
"K'ohme Humans", "Vila", "Dawen", "Tara", "Dugrani", "Ulfeid Humans", "Changeling",
               "Karskar", "Kaigen", "Qawyun", "Saelni", "Wistful Dwarves", "Draviaborn", "Goblins",
               "Tieflings", "Aasimar", "Halfgoblin", "Saplings", "Genasi", "Azatiens", "Nesir'is"
"""


def race(location=default_location):
    # SYNDRA
    # races = ["K'ohme Humans", "Vila", "Dawen", "Tara", "Dugrani", "Ulfeid Humans", "Changeling",
    #          "Kaigen", "Qawyun", "Wistful Dwarves", "Draviaborn", "Goblins", "Tieflings", "Aasimar",
    #          "Halfgoblin", "Genasi", "Azatiens"]
    # races_cum = [10, 12, 17, 32, 47, 49, 52,
    #              57, 67, 68, 69, 70, 72, 74,
    #              75, 76, 77]
    if location is None:
        raise TypeError
    global default_location
    default_location = location
    race_data = races['location'][location]['races']
    race_cump = races['location'][location]['cum_p']
    return random.choices(race_data, cum_weights=race_cump)[0]


def gender():
    gender = ['Male', 'Female', 'Other']
    gender_cum = [45, 90, 100]
    return random.choices(gender, cum_weights=gender_cum)[0]


def alignment():
    return random.choices(alignments, cum_weights=p_alignments)[0]


def profession():
    return random.choice(professions)


def employment():
    result = random.choices(employ, cum_weights=employ_cum)[0]
    if result == 'Professional':
        return profession()
    return result


def generateNPC(location, number=1):
    result = '>>> '
    for i in range(number):
        result += f'{race(location)} {gender()} {employment()} {alignment()}\n'
    return result


def basicNPC(number=1):
    result = ''
    for i in range(number):
        result += f'{race()} {gender()}\n'
    return result


# TODO: MAKE NAME GENERATOR 8)

# TODO: MAKE DATA IN JSON

if __name__ == '__main__':
    print(generateNPC('Syndra', 100))
