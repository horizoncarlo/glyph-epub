from flask import Flask, redirect, render_template, request, url_for

from room import Room
from util import get_base_api

app = Flask(__name__)
room = Room()

if __name__ == "__main__":
    app.run(debug=True, threaded=True)


@app.route("/")
def main(all_message=False):
    sender = request.args.get("sender", "")
    return render_template(
        "chat.html",
        api=get_base_api(),
        messages=(room.messages if all_message else room.messages[-50:]),
        sender=sender,
        theme="theme-dark",
    )


@app.route("/all")
def all():
    return main(all_message=True)


@app.get("/api/chat/send")
def send_chat():
    sender = request.args.get("sender", "").strip() or "Unknown"
    text = request.args.get("text", "")

    if text:
        room.add_message(sender, text)

    return redirect(url_for("main", sender=sender))
