import dice
import random


def rollv(number, hunger, target):
    result = dice.roll(f'{number}d10')

    to_send = get_successesv(result, hunger, target)

    return to_send


def rerollv(message: str, amount, hunger, target):
    numbers = []
    message = message[message.index('[') + 1:message.index(']')]
    str_nums = message.split(',')
    for num in str_nums:
        numbers.append(int(num))
    if hunger is not None:
        temp_numbers = numbers[:-int(hunger)]
    else:
        temp_numbers = numbers
    # range_num = 0 if hunger is None else int(hunger)

    smallest_nums = get_smallest_nums(int(amount), temp_numbers)

    for num in smallest_nums:
        numbers[numbers.index(num)] = random.randint(1, 10)

    to_send = get_successesv(numbers, hunger, target)

    return to_send


def get_smallest_nums(amount, numbers):
    numbers.sort()
    return numbers[:amount]


def get_successesv(numbers, hunger=None, target=None):
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