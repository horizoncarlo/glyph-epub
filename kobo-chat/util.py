from flask import has_request_context, request


def get_our_host():
    if has_request_context():
        return request.host_url + "api"
    return "/api"
