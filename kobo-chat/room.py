from dataclasses import dataclass, field
from datetime import datetime, timedelta
from util import format_date_with_ordinal

NAME_SYSTEM = "System"


class Room:
    def __init__(self):
        self.messages = []

        # Add our system messages, but setup our day header so the first human message gets one
        self.last_day = None
        self.add_system_message("Welcome to the chat room!")
        self.add_system_message("Be responsible and cool :)")
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
            sender=sender, text=text.capitalize().strip(), special=special
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

        self.messages.append(message)


@dataclass
class Message:
    sender: str
    text: str
    timestamp: datetime = field(default_factory=datetime.now)
    special: dict = field(
        default_factory=dict
    )  # Extensible special features like is_system, is_day, is_mega, etc.
