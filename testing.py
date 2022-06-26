import scheduling
import dnd


def test_timecode():
    assert scheduling.timecode('2022', '6', '25', '18', '0') == '<t:1656180000>'


def test_get_successes():
    assert dnd.get_successes(
        [6, 6, 5, 3, 2, 1, 10, 9, 10, 10]) == 'Roll: `[6, 6, 5, 3, 2, 1, 10, 9, 10, 10]` Successes: 7'  # 7
    assert dnd.get_successes(
        [6, 6, 5, 3, 2, 1, 10, 9, 10, 10], 5) == 'Roll: `[6, 6, 5, 3, 2, 1, 10, 9, 10, 10]` Successes: 7'
    assert dnd.get_successes(
        [6, 6, 5, 3, 2, 1, 10, 9, 10, 10], 5,
        7) == 'Roll: `[6, 6, 5, 3, 2, 1, 10, 9, 10, 10]` Successes: 7 **Messy Critical!**'
    assert dnd.get_successes(
        [10, 10, 5, 3, 10, 1, 2, 9, 6, 6], 5,
        7) == 'Roll: `[10, 10, 5, 3, 10, 1, 2, 9, 6, 6]` Successes: 7 **Success!**'
    assert dnd.get_successes(
        [10, 10, 5, 3, 10, 6, 2, 9, 6, 1], 5,
        8) == 'Roll: `[10, 10, 5, 3, 10, 6, 2, 9, 6, 1]` Successes: 7 **Bestial Failure!**'
    assert dnd.get_successes(
        [10, 10, 5, 1, 10, 3, 2, 9, 6, 6], 5,
        8) == 'Roll: `[10, 10, 5, 1, 10, 3, 2, 9, 6, 6]` Successes: 7 **Failure!**'


if __name__ == '__main__':
    test_timecode()
    print("Timecode test passed.")
    test_get_successes()
    print("Get_successes test passed.")
