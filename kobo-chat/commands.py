import random
import threading
from datetime import datetime

from util import fetch_public_api

COMMANDS = {}
pong_count = 0


def check_limit(room, limited_command_name, limit_cap):
    room.limits[limited_command_name] += 1

    if room.limits[limited_command_name] > limit_cap:
        room.add_system_message(f"Used up /{limited_command_name}, try again tomorrow!")
        return False
    return True


def command(name, silent=True):
    def decorator(func):
        func._silent = silent
        COMMANDS[name] = func
        return func

    return decorator


@command("help", silent=False)
def help(room, sender, args):
    room.add_system_message(
        f"Available commands: <small>{', '.join(sorted(COMMANDS.keys()))}</small>"
    )


@command("ping", silent=False)
def ping(room, sender, args):
    global pong_count
    pong_count += 1
    room.add_system_message(f"Pong #{pong_count}")


@command("time")
def time(room, sender, args):
    room.add_system_message(f"Current time: {datetime.now().strftime('%c')}")


@command("roll")
def roll(room, sender, args):
    room.add_system_message(f"{sender} rolled a <b>{random.randint(1, 6)}</b>")


@command("coinflip")
def coinflip(room, sender, args):
    room.add_system_message(
        f"{sender} flipped a coin: <b>{'Heads' if random.choices([True, False]) else 'Tails'}</b>"
    )


@command("shrug")
def shrug(room, sender, args):
    room.add_message(sender, f"{args} ¯\\_(ツ)_/¯")


@command("fart")
def tableflip(room, sender, args):
    room.add_message(sender, f"{args} (>_<)💨 ~~~pfft!")


@command("flip")
def flip(room, sender, args):
    room.add_message(sender, f"{args} (╯°□°）╯︵ ┻━┻")


@command("unflip")
def unflip(room, sender, args):
    room.add_message(sender, f"{args} ┬─┬ノ( º _ ºノ)")


@command("sleep")
def silent(room, sender, args):
    room.add_message(sender, f"{args} [{{-_-}}] ZZZzz zz z...")


@command("hug")
def hug(room, sender, args):
    room.add_message(sender, f"{args} (っÓ‿Ó)っ")


@command("beep")
def beep(room, sender, args):
    # if not check_limit(room, "beep", 50):
    #     return

    room.add_system_message(
        # TODO The beep plays as expected, but since the page is entirely re-rendered then it plays on every subsequent message too
        #      Need to manually track or remove the script from the `room.messages` itself, maybe with a `special` flag?
        # f"<small><i>beep</i></small> <b>d[ o_0 ]b</b> <small><i>beep</i></small><script>playBeep()</script>"
        f"{args} <small><i>beep</i></small> <b>d[ o_0 ]b</b> <small><i>beep</i></small>"
    )


@command("8ball")
def fate(room, sender, args):
    # The original: https://magic-8ball.com/magic-8-ball-answers/
    magic_8_ball_responses = [
        "It is certain",
        "Reply hazy, try again",
        "Don't count on it",
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


@command("button")
def button(room, sender, args):
    room.add_system_message(
        f"<button type='button' onclick='document.body.style.backgroundColor = generateRandomColor();'>Change Background Color</button>"
    )


@command("color")
def color(room, sender, args):
    colors = [
        "Amber",
        "Apricot",
        "Aqua",
        "Aquamarine",
        "Beige",
        "Black",
        "Blue",
        "Bronze",
        "Brown",
        "Burgundy",
        "Charcoal",
        "Chocolate",
        "Coral",
        "Cream",
        "Crimson",
        "Cyan",
        "Eggplant",
        "Emerald",
        "Forest",
        "Fuchsia",
        "Gold",
        "Green",
        "Grey",
        "Indigo",
        "Ivory",
        "Khaki",
        "Lavender",
        "Lilac",
        "Lime",
        "Magenta",
        "Maroon",
        "Midnight",
        "Mint",
        "Mustard",
        "Navy",
        "Olive",
        "Orange",
        "Peach",
        "Periwinkle",
        "Pink",
        "Plum",
        "Purple",
        "Red",
        "Rose",
        "Rust",
        "Salmon",
        "Sapphire",
        "Scarlet",
        "Silver",
        "Sky",
        "Tan",
        "Teal",
        "Turquoise",
        "Violet",
        "White",
        "Yellow",
    ]

    room.add_system_message(
        f"{sender} your random color is <b>{random.choice(colors)}</b>"
    )


@command("drg")
def drg(room, sender, args):
    deep_rock_galatic_quotes = [
        "Rock on!",
        "Rock and Stone... Yeeaaahhh!",
        "Rock and Stone forever!",
        "ROCK... AND... STONE!",
        "Rock and Stone!",
        "For Rock and Stone!",
        "We are unbreakable!",
        "Rock and roll!",
        "Rock and roll and stone!",
        "That's it lads! Rock and Stone!",
        "Like that! Rock and Stone!",
        "Yeaahhh! Rock and Stone!",
        "None can stand before us!",
        "Rock solid!",
        "Rock solid!",
        "Stone and Rock! ...Oh, wait...",
        "Come on guys! Rock and Stone!",
        "If you don't Rock and Stone, you ain't comin' home!",
        "We fight for Rock and Stone!",
        "We rock!",
        "Rock and Stone everyone!",
        "Stone.",
        "Yeah, yeah, Rock and Stone.",
        "Rock and Stone in the Heart!",
        "For Teamwork!",
        "Did I hear a Rock and Stone?",
        "Rock and Stone, Brother!",
        "Rock and Stone to the Bone!",
        "For Karl!",
        "Leave No Dwarf Behind!",
        "By the Beard!",
    ]

    room.add_system_message(
        f"<big>DWARF {sender}</big>: <i>{random.choice(deep_rock_galatic_quotes)}</i>"
    )


@command("rps", silent=False)
def rps(room, sender, args):
    possible_throws = ["rock", "paper", "scissors"]

    if not args or len(args.strip()) == 0:
        args = random.choice(possible_throws)
    elif (
        args.lower() != "rock"
        and args.lower() != "paper"
        and args.lower() != "scissors"
    ):
        args = random.choice(possible_throws)

    human_choice = args.upper()
    robot_choice = random.choice(possible_throws).upper()

    if human_choice == robot_choice:
        winner = "a tie"
    elif (
        (human_choice == "ROCK" and robot_choice == "SCISSORS")
        or (human_choice == "PAPER" and robot_choice == "ROCK")
        or (human_choice == "SCISSORS" and robot_choice == "PAPER")
    ):
        winner = sender
    else:
        winner = "System"

    room.add_system_message(
        f"Shoot! {sender} threw {human_choice} and System threw {robot_choice}. Winner is <b>{winner}</b>!"
    )


@command("total")
def total(room, sender, args):
    room.add_system_message(
        f"There have been <b>{len(room.messages)}</b> messages in the chat so far"
    )


@command("uptime")
def uptime(room, sender, args):
    now = datetime.now()
    delta = now - room.created_at

    total_seconds = int(delta.total_seconds())
    total_minutes = total_seconds // 60
    total_hours = total_seconds // 3600
    total_days = total_seconds // 86400

    room.add_system_message(
        f"Chat up for {total_seconds} seconds or {total_minutes} minutes or {total_hours} hours or {total_days} days"
    )


@command("stoic")
def stoic(room, sender, args):
    if not check_limit(room, "stoic", 20):
        return

    def fetch():
        data = fetch_public_api(
            room, "stoic quote", "https://stoic.tekloon.net/stoic-quote"
        )

        quote = data.get("data", {}).get("quote")

        if quote:
            room.add_system_message(f"Quote: <b>{quote}</b>")

    threading.Thread(target=fetch).start()


@command("advice")
def advice(room, sender, args):
    if not check_limit(room, "advice", 20):
        return

    def fetch():
        data = fetch_public_api(room, "advice", "https://api.adviceslip.com/advice")

        advice = data.get("slip", {}).get("advice")

        if advice:
            room.add_system_message(f"Here's some advice: <b>{advice}</b>")

    threading.Thread(target=fetch).start()


@command("dog")
def dog(room, sender, args):
    if not check_limit(room, "dog", 20):
        return

    def fetch():
        data = fetch_public_api(
            room, "dog picture", "https://dog.ceo/api/breeds/image/random"
        )

        image = data.get("message", {})

        if image:
            room.add_system_message(
                f"<img src='{image}' style='max-width: 80%;'></img>"
            )

    threading.Thread(target=fetch).start()


@command("weather")
def weather(room, sender, args):
    if not check_limit(room, "weather", 50):
        return

    def fetch():
        data = fetch_public_api(
            room,
            "weather",
            "https://api.open-meteo.com/v1/forecast?latitude=51.0447&longitude=-114.0719&current=temperature_2m",
        )

        temperature = data.get("current", {}).get("temperature_2m")

        if temperature:
            room.add_system_message(
                f"Current temperature is <b>{temperature}</b> degrees Celsius"
            )

    threading.Thread(target=fetch).start()
