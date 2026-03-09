import random
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Set

from commands import COMMANDS
from util import format_date_with_ordinal


class Room:
    join_messages = [
        "Legendary {sender} joined the room",
        "Epic {sender} just arrived",
        "Cool dude {sender} skateboarded in",
        "Mighty {sender} has entered",
        "The one and only {sender} is here",
        "Champion {sender} joins the fray",
        "Awesome {sender} made it",
        "Rockstar {sender} just popped in",
        "Heroic {sender} appears mysteriously",
        "Supreme {sender} has landed",
        "Fearless {sender} storms the chat",
        "Brilliant {sender} graces us with their presence",
        "Savage {sender} just burst through the door",
        "Ninja {sender} sneaks in",
        "Wizard {sender} conjures their presence",
        "Boss {sender} takes the stage",
        "Trailblazer {sender} enters boldly",
        "Mastermind {sender} cracks the code of entry",
        "Slimy {sender} slurps in suspiciously",
        "Adventurer {sender} embarks on the chat quest",
    ]

    def __init__(self):
        self.maxinput = 150  # Max chat message input
        self.admin_name = "System"
        self.created_at = datetime.now()
        self.messages = []

        # List of who is in the chat, loosely maintained
        self.clients: Dict[int, Client] = {}
        self.expire_client_after_min = 5

        # Various limits, which are cleared at the start of every new day
        self.limits = defaultdict(int)

        # Various banned names - pretty simple to change your name to avoid, mostly just to bug the kids
        self.banned: Set[str] = set()

        # Add our System messages, but setup our day header so the first human message gets one
        self.last_day = None
        self.add_system_message("Welcome to the chat room!")
        self.add_system_message("Be responsible and cool :)")
        self.add_system_message(
            "/help can be used to show fun commands, like /name [You]"
        )  # Show commands initially
        self.last_day = datetime.now() - timedelta(days=1)

    def change_day(self, message):
        self.last_day = message.timestamp if message else datetime.now()
        self.add_day_message()

        # Reset our limits and banned list at the start of each new day
        self.limits = defaultdict(int)
        self.banned = set()

    # Track an active client (or add them to the room list)
    def maintain_client_activity(self, client_id, sender):
        if not client_id:
            return

        if client_id not in self.clients:
            if sender != "Unknown":
                self.add_system_message(
                    "<span class='system-sender'>JOIN:</span> "
                    + random.choice(self.join_messages).format(
                        sender=f"<b>{sender}</b>"
                    )
                )
            self.clients[client_id] = Client(client_id, sender)
        else:
            self.clients[client_id].last_active = datetime.now()
            if sender:
                self.clients[client_id].sender = sender

    # Check for any expired clients and remove them
    # Currently this is only done on-demand via the /who (aka who's online) command
    # This could easily be a scheduled task though
    def check_client_activity(self):
        now = datetime.now()
        for client_id in list(self.clients):
            if now - self.clients[client_id].last_active > timedelta(
                minutes=self.expire_client_after_min
            ):
                self.clients.pop(client_id)

    def add_system_message(self, text):
        self.add_message(self.admin_name, text, is_system=True)

    def add_day_message(self):
        self.add_message(None, format_date_with_ordinal(self.last_day), is_day=True)

    def add_message(self, _sender, _text, **_special):
        # Get any hooligans pretending to be System outta here
        if (
            not _special.get("is_system")
            and _sender
            and _sender.lower() == self.admin_name.lower()
        ):
            _sender = "Faker"

        # Enforce the ban list
        if _sender in self.banned:
            return

        message = Message(
            sender=_sender,
            text=(
                _text
                if _special.get("is_system")
                else _text[0].upper() + _text[1:].strip()
            ),
            special=_special,
        )

        # How to get big font
        if message.text.lower().startswith("mega"):
            message.text = message.text[4:]
            message.special["is_mega"] = True

        # Determine if we need a new day header
        if not message.special.get("is_day") and self.last_day:
            if format_date_with_ordinal(message.timestamp) != format_date_with_ordinal(
                self.last_day
            ):
                self.change_day(message)

        # Clear timestamp if we're a System message
        if message.special.get("is_system"):
            message.timestamp = None

        # Handle various slash commands
        if message.text.startswith("/"):
            parts = message.text.split(maxsplit=1)
            command = parts[0][
                1:
            ]  # Command is the first split, then we remove the slash too

            func = COMMANDS.get(
                command.lower()
            )  # Ensure case insensitivity for commands
            if func:
                # Unless marked Silent, show the input too
                if not getattr(func, "_silent", False):
                    self.messages.append(message)

                args = parts[1] if len(parts) > 1 else ""
                if args.startswith("/"):
                    args = args[1:]

                func(self, message.sender, args)
                return

        self.messages.append(message)


@dataclass
class Message:
    sender: str
    text: str
    timestamp: datetime = field(default_factory=datetime.now)
    special: dict = field(
        default_factory=dict
    )  # Extensible special features like is_system, is_day, is_mega, etc.


@dataclass
class Client:
    client_id: int
    sender: str
    last_active: datetime = field(default_factory=datetime.now)
