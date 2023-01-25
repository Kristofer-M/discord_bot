import dice

def rollm(number, success_criteria):
    numbers = dice.roll(f'{number}d10')

    result = get_successesm(numbers, success_criteria)

    return result


def get_successesm(numbers, success_criteria):
    num_success = 0

    for number in numbers:
        if number >= success_criteria:
            num_success += 1
            if number == 10:
                numbers.append(int(dice.roll("1d10")))
        if number == 1:
            num_success -= 1

    to_send = f'Roll: `{numbers}` Successes: {num_success}'

    return to_send