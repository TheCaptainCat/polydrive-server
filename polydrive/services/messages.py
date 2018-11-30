from flask import jsonify


class ApiMessage:
    def __init__(self, **kwargs):
        self.code = kwargs.get('code', 200)
        self.status = kwargs.get('status', 'OK')
        self.messages = kwargs.get('messages', [])
        if not isinstance(self.messages, list):
            self.messages = [self.messages]
        self.content = kwargs.get('content', None)

    def http_format(self):
        json = {
            'code': self.code,
            'status': self.status,
            'messages': self.messages
        }
        if self.content is not None:
            json['content'] = self.content
        return jsonify(json), self.code


def build_message(code, status, messages=None, content=None):
    return ApiMessage(code=code, status=status, messages=messages, content=content).http_format()


def ok(messages=None, content=None):
    return build_message(200, 'OK', messages, content)


def created(messages=None, content=None):
    return build_message(201, 'CREATED', messages, content)


def bad_request(messages=None, content=None):
    return build_message(400, 'BAD REQUEST', messages, content)


def unauthorized(messages=None, content=None):
    return build_message(401, 'UNAUTHORIZED', messages, content)


def not_found(messages=None, content=None):
    return build_message(404, 'NOT FOUND', messages, content)
