from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from commands import COMMANDS
from util import format_date_with_ordinal


class Room:
    def __init__(self):
        self.maxinput = 150  # Max chat message input
        self.admin_name = "System"

        self.messages = []
        self.created_at = datetime.now()

        # Various limits, which are cleared at the start of every new day
        self.limits = defaultdict(int)

        # Various banned names - pretty simple to change your name to avoid, mostly just to bug the kids
        self.banned = set()

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
