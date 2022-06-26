import json
import math
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
        spell_name = find_spell(spell_name, spell_data)
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
    dnd_spells = open('dndspells.json')
    spell_data = json.load(dnd_spells)
    spells = re.findall(word_regex, expression)
    try:
        spells.remove('d')
    except ValueError:
        pass
    for spell in spells:
        die = find_spell_dice(spell, spell_data)
        if die is None:
            continue
        expression = expression.replace(spell, die)

    dnd_spells.close()

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


def find_spell(spell_name, spell_data):
    for spell_item in spell_data['spell'].keys():
        if spell_name in spell_item:
            return spell_item
    return None


def spell(spell_name):
    spell_name = spell_name.lower()
    with open('dndspells.json', mode='r') as spell_file:
        spell_data = json.load(spell_file)
        try:
            spell = spell_data["spell"][spell_name]
        except KeyError:
            temp = find_spell(spell_name, spell_data)
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


def rollv(number, hunger, target):
    result = dice.roll(f'{number}d10')

    to_send = get_successes(result, hunger, target)

    return to_send


# def testv(numbers, hunger=None):
#     num_success = 0
#     num_crits = 0
#     for number in numbers:
#         if number >= 6:
#             num_success += 1
#             if number == 10:
#                 num_crits += 1
#                 if num_crits % 2 == 0:
#                     num_success += 2
#         elif number == 1:
#             num_success -= 1
#
#     to_send = f'Roll: `{numbers}` Successes: {num_success}'
#
#     if hunger is not None:
#         hunger_result = None
#         hunger_roll = numbers[-1:-hunger - 1:-1]
#         if 1 in hunger_roll:
#             hunger_result = 'Bestial Failure!'
#         if 10 in hunger_roll:
#             hunger_result = 'Messy Critical!'
#         if hunger_result is not None:
#             to_send += f' **{hunger_result}**'
#
#     return to_send


def rerollv(message, amount, hunger, target):
    numbers = []
    for char in message:
        if char == ']':
            break
        if str.isdigit(char):
            numbers.append(int(char))

    range_num = 0 if hunger is None else int(hunger)

    smallest_nums = get_smallest_nums(amount, numbers, range_num)

    for num in smallest_nums:
        numbers[numbers.index(num)] = random.randint(1, 10)

    to_send = get_successes(numbers, hunger, target)

    return to_send


def get_smallest_nums(amount, numbers, range_num):
    smallest_nums = []
    for i in range(len(numbers) - range_num):
        if len(smallest_nums) < int(amount):
            smallest_nums.append(numbers[i])
        else:
            for j in range(len(smallest_nums)):
                if numbers[i] < smallest_nums[j]:
                    smallest_nums[j] = numbers[i]
                    break
    return smallest_nums


def get_successes(numbers, hunger=None, target=None):
    num_success = 0
    num_crits = 0
    for number in numbers:
        if number >= 6:
            num_success += 1
            if number == 10:
                num_crits += 1
                if num_crits % 2 == 0:
                    num_success += 2
        elif number == 1:
            num_success -= 1

    to_send = f'Roll: `{numbers}` Successes: {num_success}'

    if hunger is not None and target is not None:
        hunger = int(hunger)
        target = int(target)
        hunger_roll = numbers[-1:-hunger - 1:-1]

        if num_success >= target:
            hunger_result = 'Messy Critical!' if 10 in hunger_roll and num_crits > 0 else 'Success!'
        else:
            hunger_result = 'Bestial Failure!' if 1 in hunger_roll else 'Failure!'

        to_send += f' **{hunger_result}**'

    return to_send

if __name__ == '__main__':
    print(roll("1d10 * 2d10"))
# print(testv([10, 5, 6, 10, 2, 1, 2], 2))
