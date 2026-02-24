from flask import Flask, render_template, request, redirect, url_for
from util import get_our_host

app = Flask(__name__)
messages = [
    {"sender": "System", "text": "Welcome to the chat room!"},
    {"sender": "System", "text": "Be responsible and cool :)"},
]

if __name__ == "__main__":
    app.run(debug=True, threaded=True)


@app.route("/")
def main(all_message=False):
    sender = request.args.get("sender", "")
    return render_template(
        "chat.html",
        api=get_our_host(),
        messages=(messages if all_message else messages[-50:]),
        sender=sender,
    )


@app.route("/all")
def all():
    return main(all_message=True)


@app.get("/api/chat/send")
def send_chat():
    sender = request.args.get("sender", "").strip() or "Unknown"
    text = request.args.get("text", "")

    if text:
        messages.append({"sender": sender, "text": text.capitalize()})

    return redirect(url_for("main", sender=sender))
