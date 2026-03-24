import html
import os
import secrets

from flask import (Flask, Response, redirect, render_template, request,
                   session, stream_with_context, url_for)

from room import Room
from util import generate_client_id, get_base_api

app = Flask(__name__)
app.secret_key = os.environ.get("GLYPH_SECRET_KEY") or secrets.token_hex(8)
app.jinja_env.optimized = True
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.jinja_env.auto_reload = False

room = Room()

if __name__ == "__main__":
    app.run(debug=True, threaded=True)


@app.before_request
def ensure_client_id():
    session.permanent = True  # Doesn't work on Kobo, just resets on new browser open
    if "client_id" not in session:
        session["client_id"] = generate_client_id()


@app.route("/")
def main(all_message=False):
    sender = _get_sender(request)

    # Maintain that this client is active
    room.maintain_client_activity(session["client_id"], sender)

    # Determine if we're coming from a Kobo Clara browser, which has some different format and CSS/JS limitations
    is_kobo = (
        "kobo" in (request.user_agent or request.headers.get("User-Agent", "")).lower()
    )

    return render_template(
        "chat.html",
        api=get_base_api(),
        messages=(room.messages if all_message else room.messages[-50:]),
        sender=sender,
        maxinput=room.maxinput,
        admin_name=room.admin_name,
        theme="theme-light",
        is_kobo=is_kobo,
    )


@app.route("/all")
def all():
    return main(all_message=True)


@app.route(get_base_api() + "/chat/stream")
def chat_stream():
    last_index = len(room.messages)

    def event_stream():
        nonlocal last_index

        yield ": connected\n\n"

        while True:
            with room.perform_sse:
                room.perform_sse.wait()

            while last_index < len(room.messages):
                message = room.messages[last_index]
                last_index += 1

                row = render_template(
                    "includes/chat_row.html",
                    message=message,
                    admin_name=room.admin_name,
                ).replace("\n", "")

                yield f"data: {row}\n\n"

    return Response(
        stream_with_context(event_stream()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # For Nginx to send right away
        },
    )


@app.post(get_base_api() + "/chat/send")
def send_chat():
    text = request.form.get("text")
    sender = _get_sender(request)

    if text:
        room.add_message(sender, text)

        # Really special case due to scoping
        # If we requested a name change store it here
        if text.lower().startswith("/name"):
            args = text.split()
            if len(args) > 1:
                sender = html.escape(" ".join(args[1:])).strip()

    return redirect(url_for("main", sender=sender))


def _get_sender(request):
    sender = request.form.get("sender") or request.args.get("sender") or "Unknown"
    sender = html.escape(sender).strip()

    # Avoid trickery
    if sender.startswith("/"):
        sender = sender[1:]

    return sender
