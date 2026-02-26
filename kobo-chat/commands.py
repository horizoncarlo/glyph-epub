import json
import random
import threading
import urllib.request
from datetime import datetime

COMMANDS = {}
pong_count = 0

# TODO Command ideas:
# Change name from an input to a /name command. Keep in URL as state
# Jokes from dataset: https://github.com/amoudgl/short-jokes-dataset/blob/master/data/reddit-cleanjokes.csv
# Fortune cookie (...find a dataset)
# Change background color randomly. See also theme-light and theme-dark. Currently not setup per-user really
# Start a vote (for simplicity only one at a time)
# Math or calculator for input?
# Rock paper scissors, put your choice, then a bot randomizes and chooses the winner
# Some kind of light "fight monster" mode? Randomly attack, rolling dice, with health


def command(name, silent=False):
    def decorator(func):
        func._silent = silent
        COMMANDS[name] = func
        return func

    return decorator


@command("help")
def help(room, sender, args):
    room.add_system_message(f"Available commands: {', '.join(sorted(COMMANDS.keys()))}")


@command("ping")
def ping(room, sender, args):
    global pong_count
    pong_count += 1
    room.add_system_message(f"Pong #{pong_count}")


@command("coinflip", silent=True)
def coinflip(room, sender, args):
    room.add_system_message(
        f"{sender} flipped a coin: <b>{'Heads' if random.choices([True, False]) else 'Tails'}</b>"
    )


@command("time", silent=True)
def time(room, sender, args):
    room.add_system_message(f"Current time: {datetime.now().strftime('%c')}")


@command("roll", silent=True)
def roll(room, sender, args):
    room.add_system_message(f"{sender} rolled a <b>{random.randint(1, 6)}</b>")


@command("shrug", silent=True)
def shrug(room, sender, args):
    room.add_message(sender, "¯\\_(ツ)_/¯")


@command("fart", silent=True)
def tableflip(room, sender, args):
    room.add_message(sender, "(>_<)💨 ~~~pfft!")


@command("tableflip", silent=True)
def tableflip(room, sender, args):
    room.add_message(sender, "(╯°□°）╯︵ ┻━┻")


@command("sleep", silent=True)
def silent(room, sender, args):
    room.add_message(sender, "[{-_-}] ZZZzz zz z...")


@command("hug", silent=True)
def hug(room, sender, args):
    room.add_message(sender, "(っ◕‿◕)っ")


@command("8ball", silent=True)
def fate(room, sender, args):
    # The original: https://magic-8ball.com/magic-8-ball-answers/
    magic_8_ball_responses = [
        "It is certain",
        "Reply hazy, try again",
        "Don’t count on it",
        "It is decidedly so",
        "Ask again later",
        "My reply is no",
        "Without a doubt",
        "Better not tell you now",
        "My sources say no",
        "Yes definitely",
        "Cannot predict now",
        "Outlook not so good",
        "You may rely on it",
        "Concentrate and ask again",
        "Very doubtful",
        "As I see it, yes",
        "Most likely",
        "Outlook good",
        "Yes",
        "Signs point to yes",
    ]

    room.add_system_message(
        f"Magic 8 Ball says to {sender}: <b>{random.choice(magic_8_ball_responses)}</b>"
    )


@command("dog", silent=True)
def dog(room, sender, args):
    room.add_system_message("Fetching dog picture...be sure to Refresh after")

    def fetch():
        try:
            url = "https://dog.ceo/api/breeds/image/random"
            with urllib.request.urlopen(url, timeout=5) as resp:
                data = json.load(resp)
            image = data.get("message", {})

            if image:
                room.add_system_message(
                    f"<img src='{image}' style='max-width: 80%;'></img>"
                )

            return
        except Exception as e:
            pass

        room.add_system_message("Failed to get a random dog picture :(")

    threading.Thread(target=fetch).start()


@command("weather", silent=True)
def weather(room, sender, args):
    room.add_system_message("Fetching weather...be sure to Refresh after")

    # Run off thread so we don't block everything
    def fetch():
        try:
            url = "https://api.open-meteo.com/v1/forecast?latitude=51.0447&longitude=-114.0719&current=temperature_2m"
            with urllib.request.urlopen(url, timeout=3) as resp:
                data = json.load(resp)
            temperature = data.get("current", {}).get("temperature_2m")

            if temperature:
                room.add_system_message(
                    f"Current temperature is <b>{temperature}</b> degrees Celsius"
                )

            return
        except Exception as e:
            pass

        room.add_system_message("Failed to get current weather :(")

    threading.Thread(target=fetch).start()
