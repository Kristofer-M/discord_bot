import asyncio
import random
import datetime
import discord
import os
from asyncio import AbstractEventLoop

seconds_in_week = 604800
seconds_in_day = 86400


class KrisKlient(discord.Client):

    def __init__(self, loop: AbstractEventLoop):
        super().__init__()
        self.alarm_tasks = {}
        self.loop = loop
        self.days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        self.puns = [
            "What happened to the guy who sued over his missing luggage? He lost his case.",
            "How did you get hit on the head with a book? I only have my shelf to blame.",
            "What did one blade of grass say to another about the lack of rain? I guess we'll just have to make dew.",
            "I used to be addicted to soap, but I'm clean now."
        ]

    async def on_ready(self):
        print("Logged in as {0}".format(self.user))

    async def on_message(self, message):
        loop = self.loop

        if message.author == self.user:
            return

        if 'thanos' in str(message.content).lower():
            loop.create_task(self.send_thanos(message))

        if message.content.startswith("!"):
            parsed_message_content = str(message.content).split()
            command = parsed_message_content[0][1:]
            if command == "alarm":
                loop.create_task(self.alarm(message))

            elif command == "hello":
                loop.create_task(self.hello(message))

            elif command == "pun":
                loop.create_task(self.pun(message))

            elif command == "stop":
                loop.create_task(self.stop(message))

            elif command == "stopall":
                loop.create_task(self.stopall(message))

            else:
                await message.channel.send("Unknown command.")

    async def get_alarm_vars(self, message):
        parsed_message_content = str(message.content).split()
        if len(parsed_message_content) < 5:
            await message.channel.send("More arguments required.")
            return None

        try:
            alarm_day = parsed_message_content[1]
            day = self.days.index(alarm_day)

            alarm_hour = parsed_message_content[2]
            hour = alarm_hour.split(":")[0]
            minutes = alarm_hour.split(":")[1]
            alarm_time = datetime.time(int(hour), int(minutes))


            alarm = f'{alarm_day} {alarm_hour}'
        except ValueError as v:
            if 'list' in str(v):
                v = str(v).split(" ")[0]
                v += ' is not a day.'
            await message.channel.send(v)
            return None
        except IndexError:
            await message.channel.send("Please enter time in HH:MM format.")
            return None

        args = parsed_message_content[3:]
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
            'day': day,
        }

    async def send_thanos(self, message):
        with open('thanos_smile.jpg', 'rb') as fp:
            to_send = discord.File(fp, 'thanos.jpg')
            await message.channel.send(file=to_send)

    async def pun(self, message):
        await message.channel.send(random.choice(self.puns))

    async def hello(self, message):
        await message.channel.send("Hello!")

    async def alarm(self, message):
        dt = datetime.datetime
        alarm_vars = await self.get_alarm_vars(message)
        if alarm_vars is None:
            return

        day_a = alarm_vars['day']
        day_b = self.days.index(dt.now().strftime("%A").lower())

        if day_a >= day_b:
            day_delta = day_a - day_b
        else:
            day_delta = 7 - abs(day_a - day_b)
        day_delta = day_delta * seconds_in_day

        alarm_time = alarm_vars['alarm_time']
        start_time = datetime.time(dt.now().hour, dt.now().minute)

        time_delta = dt.combine(dt.today(), alarm_time) - dt.combine(dt.today(), start_time)

        alarm = alarm_vars['alarm']
        await message.channel.send("Alarm set for {0}".format(str(alarm)))
        wait_time = (time_delta.seconds - dt.now().second) + day_delta

        alarm_name = alarm_vars['alarm_name']
        user_names = alarm_vars['user_names']
        self.alarm_tasks[alarm_name] = self.loop.create_task(self.repeat_weekly(message, alarm_name, user_names, wait_time))

    async def repeat_weekly(self, message, alarm_name, user_names, wait_time):
        while True:
            await asyncio.sleep(wait_time)
            await message.channel.send(f'DING-DING-DING-DING-DING {alarm_name} {user_names}')
            wait_time = seconds_in_week

    async def stop(self, message):
        parsed_message_content = str(message.content).split()
        if len(parsed_message_content) < 2:
            await message.channel.send("More arguments required.")
            return
        else:
            alarm_name = " ".join(parsed_message_content[1:])
            self.alarm_tasks = self.alarm_tasks
            self.alarm_tasks[alarm_name].cancel()
            await message.channel.send(f'{alarm_name} stopped.')

    async def stopall(self, message):
        for alarm_name in self.alarm_tasks:
            self.alarm_tasks[alarm_name].cancel()
        await message.channel.send("All alarms stopped.")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    client = KrisKlient(loop=loop)
    client.run(os.getenv('DISCORD_BOT_TOKEN'))
