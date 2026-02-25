from dataclasses import dataclass, field
from datetime import datetime, timedelta

from commands import COMMANDS
from util import format_date_with_ordinal

NAME_SYSTEM = "System"


class Room:
    def __init__(self):
        self.messages = []

        # Add our System messages, but setup our day header so the first human message gets one
        self.last_day = None
        self.add_system_message("Welcome to the chat room!")
        self.add_system_message("Be responsible and cool :)")
        self.add_system_message(
            "/help can be used to show fun commands"
        )  # Show commands initially
        self.last_day = datetime.now() - timedelta(days=1)

    def add_system_message(self, text):
        self.add_message(NAME_SYSTEM, text, is_system=True)

    def add_day_message(self):
        self.add_message(None, format_date_with_ordinal(self.last_day), is_day=True)

    def add_message(self, sender, text, **special):
        # Get any hooligans pretending to be System outta here
        if (
            not special.get("is_system")
            and sender
            and sender.lower() == NAME_SYSTEM.lower()
        ):
            sender = "Faker"

        message = Message(
            sender=sender,
            text=text if special.get("is_system") else text.capitalize().strip(),
            special=special,
        )

        # How to get big font
        if text.lower().startswith("mega"):
            text = text[4:]
            special["is_mega"] = True

        # Determine if we need a new day header
        if not special.get("is_day") and self.last_day:
            if format_date_with_ordinal(message.timestamp) != format_date_with_ordinal(
                self.last_day
            ):
                self.last_day = message.timestamp
                self.add_day_message()

        # Clear timestamp if we're a System message
        if special.get("is_system"):
            message.timestamp = None

        # Handle various slash commands
        if text.startswith("/"):
            parts = text.split(maxsplit=1)
            command = parts[0][
                1:
            ]  # Command is the first split, then we remove the slash too

            func = COMMANDS.get(command)
            if func:
                # Unless marked Silent, show the input too
                if not getattr(func, "_silent", False):
                    self.messages.append(message)
                args = parts[1] if len(parts) > 1 else ""
                func(self, sender, args)
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
