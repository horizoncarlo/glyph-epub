import ast
import html
import operator as op
import random
from datetime import datetime
from threading import Thread, Timer

from flask import session

from util import check_limit, check_unsafe_pass, fetch_public_api

COMMANDS = {}
CALC_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.USub: op.neg,
}
HIGH_FIVE_TIMEOUT_S = 60
VOTE_TIMEOUT_S = 60 * 60  # 1 hour

pong_count = 0
high_five_waiting = None  # Set to an initial sender if they try to highfive
high_five_timer = None

vote_text = None
vote_count = {}
vote_timer = None


def command(name, silent=True):
    def decorator(func):
        func._silent = silent
        COMMANDS[name.lower()] = func
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
    room.add_system_message(
        f"{sender} the current time is {datetime.now().strftime('%c')}"
    )


@command("who", silent=False)
def who(room, sender, args):
    room.check_client_activity()

    if len(room.clients) <= 1:
        room.add_system_message(
            f"Just YOU online in the last {room.expire_client_after_min} minutes <small>(so lonely in here...)</small>"
        )
    else:
        clients_fmt = ", ".join(client.sender for client in room.clients.values())
        room.add_system_message(
            f"{len(room.clients)} people online in the last {room.expire_client_after_min} minutes: {clients_fmt}"
        )


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


@command("fish")
def fish(room, sender, args):
    room.add_message(
        sender,
        f"{args} ¸.·´¯`·.´¯`·.¸¸.·´¯`·.¸><(((º> (caught a {random.randint(1, 50)} pounder!)",
    )


@command("hug")
def hug(room, sender, args):
    room.add_message(sender, f"(っÓ‿Ó)っ {args} (っÓ‿Ó)っ")


@command("cheer")
def cheer(room, sender, args):
    room.add_message(sender, f"{args} ^(¤o¤)^")


@command("b")
def bold(room, sender, args):
    room.add_message(sender, f"<b>{html.escape(args)}</b>", is_safe=True)


@command("i")
def italic(room, sender, args):
    room.add_message(sender, f"<i>{html.escape(args)}</i>", is_safe=True)


@command("u")
def underline(room, sender, args):
    room.add_message(sender, f"<u>{html.escape(args)}</u>", is_safe=True)


@command("html")
def html_command(room, sender, args):
    if args:
        split_args = args.split()
        if len(split_args) > 1:  # Need at least the Password and some text
            user_guess = split_args[0]
            if check_unsafe_pass(room, user_guess):
                room.add_message(sender, " ".join(split_args[1:]), is_safe=True)
                return
            else:
                room.add_system_message(
                    f"{sender} failed to authorize for /html, nice try!"
                )
                return
    room.add_system_message(
        f"{sender} incorrectly tried a command. Use /html [password] [text]"
    )


@command("beep")
def beep(room, sender, args):
    # if not check_limit(room, "beep", 50):
    #     return

    room.add_message(
        sender,
        # TODO The beep plays as expected, but since the page is entirely re-rendered then it plays on every subsequent message too
        #      Need to manually track or remove the script from the `room.messages` itself, maybe with a `special` flag?
        # f"<small><i>beep</i></small> <b>d[ o_0 ]b</b> <small><i>beep</i></small><script>playBeep()</script>"
        f"{html.escape(args)} <small><i>beep</i></small> <b>d[ o_0 ]b</b> <small><i>beep</i></small>",
        is_safe=True,
    )


@command("8ball")
def fate(room, sender, args):
    if not args or len(args.strip()) == 0:
        args = "A secret"

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
        f"{sender} asks Magic 8 Ball: <i>{html.escape(args)}</i> and the answer is <b>{random.choice(magic_8_ball_responses)}</b>"
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


@command("ban", silent=False)
def ban(room, sender, args):
    if not args or len(args.strip()) == 0 or sender == args:
        return

    if args not in room.banned:
        room.banned.add(args)
        room.add_system_message(f"{sender} BANNED {html.escape(args)} (╯︵╰,)")


@command("name")
def name(room, sender, args):
    if not args or len(args.strip()) == 0:
        room.add_system_message(
            f"Your current name is {sender} - enter a new name with the command to change"
        )
    else:
        room.add_system_message(f"{sender} tried to rename to {html.escape(args)}")


@command("banlist", silent=False)
def banlist(room, sender, args):
    if len(room.banned) > 0:
        room.add_system_message(
            f"<u>Banlist</u><br/>{html.escape(', '.join(room.banned))}"
        )
    else:
        room.add_system_message(
            "No one is banned! <small><i>(friendly bunch here...)</i></small>"
        )


@command("unban", silent=False)
def unban(room, sender, args):
    if not args or len(args.strip()) == 0 or sender == args:
        return

    if args in room.banned:
        room.banned.discard(args)
        room.add_system_message(f"{sender} UNBANNED {html.escape(args)} 【ツ】")


@command("total", silent=False)
def total(room, sender, args):
    room.add_system_message(
        f"There have been <b>{len(room.messages)}</b> messages in the chat so far"
    )


@command("calc", silent=False)
def calc(room, sender, args):
    if not args or len(args.strip()) == 0:
        room.add_system_message(
            f"{sender} enter a math calculation (such as 2+2) to use the /calc command"
        )
        return

    # Bit verbose, but beats the insecurity of a straight eval()
    def eval_node(node):
        if len(args) > room.maxinput:
            raise ValueError

        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError

        if isinstance(node, ast.BinOp) and type(node.op) in CALC_OPS:
            return CALC_OPS[type(node.op)](eval_node(node.left), eval_node(node.right))

        if isinstance(node, ast.UnaryOp) and type(node.op) in CALC_OPS:
            return CALC_OPS[type(node.op)](eval_node(node.operand))

        raise ValueError

    try:
        tree = ast.parse(args, mode="eval")
        res = eval_node(tree.body)

        if isinstance(res, float):
            res = round(res, 3)

        room.add_system_message(f"Answer: <b>{res:,}</b>")
    except Exception:
        room.add_system_message("Answer: <b>Error</b>")


@command("uptime", silent=False)
def uptime(room, sender, args):
    now = datetime.now()
    delta = now - room.created_at

    total_seconds = int(delta.total_seconds())
    total_minutes = total_seconds // 60
    total_hours = total_seconds // 3600
    total_days = total_seconds // 86400

    room.add_system_message(
        f"Chat up for {total_seconds:,} seconds or {total_minutes:,} minutes or {total_hours:,} hours or {total_days:,} days"
    )


@command("vote", silent=False)
def vote(room, sender, args):
    global vote_text, vote_timer

    if vote_text:
        room.add_system_message(
            f"Vote in progress, use /voteYES or /voteNO for <b>{vote_text}</b>"
        )
        return

    def vote_done():
        global vote_text, vote_count, vote_timer

        room.add_system_message(
            f"Vote complete! Yes: <i>{vote_count.get('yes', 0)}</i> vs No: <i>{vote_count.get('no', 0)}</i> for <b>{vote_text}</b>"
        )

        vote_text = None
        vote_count = {}
        vote_timer = None

    if not args or len(args.strip()) == 0:
        room.add_system_message(
            f"No vote in progress. Need to know what you want to vote on! Start with /vote [text]"
        )
        return

    vote_text = args
    vote_timer = Timer(VOTE_TIMEOUT_S, vote_done)
    vote_timer.start()

    session.pop("hasvoted", None)

    room.add_system_message(
        f"{sender} started a vote! Use /voteYES or /voteNO to weigh in. Results shown in <b>{VOTE_TIMEOUT_S//60} minutes</b>"
    )


@command("voteYES")
def voteyes(room, sender, args):
    _vote(room, sender, "yes")


@command("voteNO")
def voteno(room, sender, args):
    _vote(room, sender, "no")


def _vote(room, sender, vote):
    global vote_text, vote_count

    if not vote_text:
        room.add_system_message(
            f"{sender} tried to vote but there's not current vote! Use /vote [text] first"
        )
        return

    if session.get("hasvoted"):
        room.add_system_message(
            f"{sender} tried to vote again, but already has! <small>(sketchy...)</small>"
        )
        return

    room.add_system_message(f"{sender} voted in the current election!")
    vote_count[vote] = vote_count.get(vote, 0) + 1
    session["hasvoted"] = True


@command("highfive")
def highfive(room, sender, args):
    global high_five_waiting, high_five_timer

    if high_five_waiting:
        if high_five_waiting == sender:  # Can't high five yourself
            return

        room.add_system_message(
            f"{sender} and {high_five_waiting} <span class='high-five'>HIGH FIVED!!! 🫸💥🫷</span>"
        )

        if high_five_timer:
            high_five_timer.cancel()
            high_five_timer = None

        high_five_waiting = None
    else:
        tip = random.choice(["Dab them up!", "Don't leave them hanging!"])
        room.add_system_message(f"{sender} is waiting for a <b>high five</b>. {tip}")
        high_five_waiting = sender

        def left_hanging():
            global high_five_waiting, high_five_timer
            room.add_system_message(
                f"{high_five_waiting} was left hanging on their <b>high five :(</b>"
            )
            high_five_waiting = None
            high_five_timer = None

        high_five_timer = Timer(HIGH_FIVE_TIMEOUT_S, left_hanging)
        high_five_timer.start()


@command("quote")
def quote(room, sender, args):
    if not check_limit(room, "quote", 20):
        return

    def fetch():
        data = fetch_public_api(
            room, sender, "stoic quote", "https://stoic.tekloon.net/stoic-quote"
        )

        quote = data.get("data", {}).get("quote")

        if quote:
            room.add_system_message(f"Quote: <b>{quote}</b>")

    Thread(target=fetch).start()


@command("advice")
def advice(room, sender, args):
    if not check_limit(room, "advice", 20):
        return

    def fetch():
        data = fetch_public_api(
            room, sender, "advice", "https://api.adviceslip.com/advice"
        )

        advice = data.get("slip", {}).get("advice")

        if advice:
            room.add_system_message(f"Advice: <b>{advice}</b>")

    Thread(target=fetch).start()


@command("dog")
def dog(room, sender, args):
    if not check_limit(room, "dog", 20):
        return

    def fetch():
        data = fetch_public_api(
            room, sender, "dog picture", "https://dog.ceo/api/breeds/image/random"
        )

        image = data.get("message", {})

        if image:
            room.add_system_message(
                f"<img src='{image}' class='api-image' alt='Random picture of a dog'>"
            )

    Thread(target=fetch).start()


@command("capy")
def capy(room, sender, args):
    if not check_limit(room, "capy", 20):
        return

    def fetch():
        data = fetch_public_api(
            room,
            sender,
            "capybara picture",
            "https://api.capy.lol/v1/capybara?json=true",
        )

        image = data.get("data", {}).get("url")

        if image:
            room.add_system_message(
                f"<img src='{image}' class='api-image' alt='Random picture of a capybara'>"
            )

    Thread(target=fetch).start()


@command("joke")
def joke(room, sender, args):
    if not check_limit(room, "joke", 30):
        return

    def fetch():
        data = fetch_public_api(room, sender, "dad joke", "https://icanhazdadjoke.com/")

        joke = data.get("joke", {})

        if joke:
            room.add_system_message(f"Joke: <b>{joke}</b>")

    Thread(target=fetch).start()


@command("weather")
def weather(room, sender, args):
    if not check_limit(room, "weather", 50):
        return

    def fetch():
        data = fetch_public_api(
            room,
            sender,
            "weather",
            "https://api.open-meteo.com/v1/forecast?latitude=51.0447&longitude=-114.0719&current=temperature_2m",
        )

        temperature = data.get("current", {}).get("temperature_2m")

        if temperature:
            room.add_system_message(
                f"Current temperature is <b>{temperature}</b> degrees Celsius"
            )

    Thread(target=fetch).start()
