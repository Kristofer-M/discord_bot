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
                alarm_vars = await self.make_alarm(parsed_message_content, message)
                try:
                    user_names = alarm_vars[0]
                    alarm_name = alarm_vars[1]
                except TypeError:
                    return
                self.alarm_tasks[alarm_name] = loop.create_task(self.alarm(message, alarm_name, user_names))

            elif command == "hello":
                loop.create_task(self.hello(message))

            elif command == "pun":
                loop.create_task(self.pun(message))

            elif command == "stop":
                if len(parsed_message_content) < 2:
                    await message.channel.send("More arguments required.")
                    return
                else:
                    alarm_name = " ".join(parsed_message_content[1:])
                    self.alarm_tasks = self.alarm_tasks
                    self.alarm_tasks[alarm_name].cancel()

            elif command == "stopall":
                for alarm_name in self.alarm_tasks:
                    self.alarm_tasks[alarm_name].cancel()

            else:
                await message.channel.send("Unknown command.")

    async def make_alarm(self, parsed_message_content: list, message):
        if len(parsed_message_content) < 5:
            await message.channel.send("More arguments required.")
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
        return [user_names, alarm_name]

    async def send_thanos(self, message):
        with open('thanos_smile.jpg', 'rb') as fp:
            to_send = discord.File(fp, 'thanos.jpg')
            await message.channel.send(file=to_send)

    async def pun(self, message):
        await message.channel.send(random.choice(self.puns))

    async def hello(self, message):
        await message.channel.send("Hello!")

    async def alarm(self, message, alarm_name, user_names):
        dt = datetime.datetime
        alarm_date = str(message.content).split()
        try:
            alarm_day = alarm_date[1]
            alarm_hour = alarm_date[2]
            alarm = f'{alarm_day} {alarm_hour}'

            hour = alarm_hour.split(":")[0]
            minutes = alarm_hour.split(":")[1]
            alarm_time = datetime.time(int(hour), int(minutes))

            day_a = self.days.index(alarm_day)
            day_b = self.days.index(dt.now().strftime("%A").lower())
        except ValueError as v:
            if 'list' in str(v):
                v = str(v).split(" ")[0]
                v += ' is not a day.'
            await message.channel.send(v)
            return
        except IndexError:
            await message.channel.send("Please enter time in HH:MM format.")
            return

        start_hour = dt.now().hour
        start_minute = dt.now().minute
        start_time = datetime.time(start_hour, start_minute)

        if day_a >= day_b:
            day_delta = day_a - day_b
        else:
            day_delta = 7 - abs(day_a - day_b)
        day_delta = day_delta * seconds_in_day

        time_delta = dt.combine(dt.today(), alarm_time) - dt.combine(dt.today(), start_time)
        await message.channel.send("Alarm set for {0}".format(str(alarm)))

        await asyncio.sleep((time_delta.seconds - dt.now().second) + day_delta)
        await message.channel.send(f'DING-DING-DING-DING-DING {alarm_name} {user_names}')

        self.alarm_tasks[alarm_name] = self.loop.create_task(self.repeat_weekly(message, alarm_name, user_names))

    async def repeat_weekly(self, message, alarm_name, user_names):
        while True:
            await asyncio.sleep(seconds_in_week)
            await message.channel.send(f'DING-DING-DING-DING-DING {alarm_name} {user_names}')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    client = KrisKlient(loop=loop)
    client.run(os.getenv('DISCORD_BOT_TOKEN'))
