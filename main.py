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
        self.allow_run = True
        self.loop = loop
        self.days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        self.puns = [
            "What happened to the guy who sued over his missing luggage? He lost his case.",
            "How did you get hit on the head with a book? I only have my shelf to blame.",
            "What did one blade of grass say to another about the lack of rain? I guess we'll just have to make dew.",
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
            command = str(message.content).split(" ")[0][1:]
            if command == "alarm":
                self.allow_run = True
                loop.create_task(self.alarm(message))
            elif command == "hello":
                loop.create_task(self.hello(message))
            elif command == "pun":
                loop.create_task(self.pun(message))
            elif command == "stop":
                self.allow_run = False
            else:
                message.channel.send("Unknown command.")

    async def send_thanos(self, message):
        with open('thanos_smile.jpg', 'rb') as fp:
            to_send = discord.File(fp, 'thanos.jpg')
            await message.channel.send(file=to_send)

    async def pun(self, message):
        await message.channel.send(random.choice(self.puns))

    async def hello(self, message):
        await message.channel.send("Hello!")

    async def check_hour(self, hour):
        numbers = hour.split(":")
        if numbers[0] == hour:
            return False
        if int(numbers[0]) < 0 or int(numbers[0]) > 24:
            return False
        if int(numbers[1]) < 0 or int(numbers[1]) > 60:
            return False
        return True

    async def alarm(self, message):
        alarm_date = str(message.content).split(" ")
        alarm_day = alarm_date[1]
        alarm_hour = alarm_date[2]

        if alarm_day.lower() not in self.days:
            await message.channel.send("Day unrecognized.")
            return
        if not await self.check_hour(alarm_hour):
            await message.channel.send("Unrecognized time format, enter time in `HH:MM` format using military hours.")
            return

        alarm = f'{alarm_day} {alarm_hour}'
        dt = datetime.datetime
        hour = alarm_hour.split(":")[0]
        minutes = alarm_hour.split(":")[1]
        alarm_time = datetime.time(int(hour), int(minutes))
        start_hour = dt.now().hour
        start_minute = dt.now().minute
        start_time = datetime.time(start_hour, start_minute)

        day_a = self.days.index(alarm_day)
        day_b = self.days.index(dt.now().strftime("%A"))
        if day_a >= day_b:
            day_delta = day_a - day_b
        else:
            day_delta = 7 - abs(day_a - day_b)

        time_delta = dt.combine(dt.today(), alarm_time) - dt.combine(dt.today(), start_time)
        time_delta += day_delta * seconds_in_day
        await message.channel.send("Alarm set for {0}".format(str(alarm)))
        await asyncio.sleep((time_delta.seconds - dt.now().second))
        if self.allow_run:
            await message.channel.send("@everyone DING-DING-DING-DING-DING")
            self.loop.create_task(self.repeat_weekly(message))

    async def repeat_weekly(self, message):
        await asyncio.sleep(seconds_in_week)
        if self.allow_run:
            await message.channel.send("@everyone DING-DING-DING-DING-DING")
            self.loop.create_task(self.repeat_weekly(message))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    client = KrisKlient(loop=loop)
    client.run(os.getenv('DISCORD_BOT_TOKEN'))
