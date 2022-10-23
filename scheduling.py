import datetime
# from dateutil import parser
from discord.ext import tasks
import asyncio
import pytz

import main

scheduled_tasks = {}


class ScheduledTask:
    def __init__(self, name, context, wait_time, schedule_name, user_names):
        self.name = name
        self.task = self.alarm_start.start(context, wait_time, schedule_name, user_names)
        self.context = context

    @tasks.loop(count=1)
    async def alarm_start(self, context, wait_time, schedule_name, user_names):
        print(f'The name of the alarm is: {schedule_name}')
        await asyncio.sleep(wait_time)
        scheduled_tasks[schedule_name] = self.repeat_weekly.start(context, schedule_name, user_names)
        self.task = scheduled_tasks[schedule_name]

    @tasks.loop(seconds=2)
    async def repeat_weekly(self, context, alarm_name, user_names):
        await main.send_message(context, f'{alarm_name} {user_names}')

    def cancel(self):
        self.task.cancel()


async def stop(context, schedule_name):
    scheduled_tasks[schedule_name].cancel()
    await main.send_message(context, f'{schedule_name} stopped.')


async def stop_all(context):
    for alarm_name in scheduled_tasks:
        scheduled_tasks[alarm_name].cancel()
    await main.send_message(context, "All alarms stopped.")


# async def alarm(context, day, time, *args):
#     dt = datetime.datetime
#     user_names = []
#     alarm_name = []
#     args = [arg for tup in args for arg in tup]
#
#     for arg in args:
#         if str(arg).startswith('<@'):
#             user_names.append(arg)
#         else:
#             alarm_name.append(arg)
#     user_names = ' '.join(user_names)
#     alarm_name = ' '.join(alarm_name)
#
#     alarm = f'{day} {time}'
#     await main.send_message(context, "Alarm set for {0}".format(str(alarm)))
#     future_date = parser.parse(alarm)
#     wait_time = future_date - dt.now()
#     wait_time = wait_time.seconds
#     print(f'The name of the alarm is: {alarm_name}')
#     scheduled_tasks[alarm_name] = ScheduledTask(alarm_name, context, wait_time, alarm_name, user_names)


def timecode(year, month, day, hour, minute):
    tem = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute),
                            tzinfo=pytz.timezone('Europe/Berlin'))
    timestamp = int(tem.timestamp())
    # timestamp = int(tem.replace(tzinfo=datetime.timezone.utc).timestamp())
    # epoch = datetime.datetime(1970, 1, 1)
    # delta = tem - epoch
    result = f'<t:{timestamp}> Unix Timestamp: `<t:{timestamp}>`'
    return result

# if __name__ == '__main__':
#     # print((int)((datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds()))
