import html

from flask import Flask, redirect, render_template, request, session, url_for

from room import Room
from util import get_base_api

app = Flask(__name__)
room = Room()

if __name__ == "__main__":
    app.run(debug=True, threaded=True)


def get_sender(request):
    sender = request.form.get("sender") or request.args.get("sender") or "Unknown"
    sender = html.escape(sender).strip()

    # Avoid trickery
    if sender.startswith("/"):
        sender = sender[1:]

    return sender


@app.route("/")
def main(all_message=False):
    sender = get_sender(request)

    ## Some general ideas if we want a unique identifier (regardless of name change) for each session
    ## Requires `app.secret_key = 'something-unique'` at top of file below Flask creation
    ## session.permanent = True  # Doesn't work on Kobo, just resets on new browser open
    # userId = session.get("userId", str(random.randint(1000, 4000))
    # session["userId"] = userId

    return render_template(
        "chat.html",
        api=get_base_api(),
        messages=(room.messages if all_message else room.messages[-50:]),
        sender=sender,
        theme="theme-light",
    )


@app.route("/all")
def all():
    return main(all_message=True)


@app.post(get_base_api() + "/chat/send")
def send_chat():
    text = request.form.get("text")
    sender = get_sender(request)

    if text:
        room.add_message(sender, text)

        # Really special case due to scoping
        # If we requested a name change store it here
        if text.lower().startswith("/name"):
            args = text.split()
            if len(args) > 1:
                sender = html.escape(" ".join(args[1:])).strip()

    return redirect(url_for("main", sender=sender))
