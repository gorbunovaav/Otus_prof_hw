#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import json
import datetime
import logging
import hashlib
import uuid
from argparse import ArgumentParser
from http.server import BaseHTTPRequestHandler, HTTPServer

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')

def get_score(store, phone, email, birthday=None, gender=None, first_name=None, last_name=None):
    score = 0
    if phone:
        score += 1.5
    if email:
        score += 1.5
    if birthday and gender:
        score += 1.5
    if first_name and last_name:
        score += 0.5
    return score

def get_interests(store, cid):
    interests = ["cars", "pets", "travel", "hi-tech", "sport", "music", "books", "tv", "cinema", "geek", "otus"]
    return random.sample(interests, 2)

class ArgumentsField(object):
    def __init__(self, required=False, nullable=False):
        self.required = required
        self.nullable = nullable

    def validate(self, value):
        if self.required and value is None:
            raise ValueError("Field is required")
        if not self.nullable and not value:
            raise ValueError("Field cannot be empty")
        return True

class CharField(ArgumentsField):
    def validate(self, value):
        super().validate(value)
        if value is not None and not isinstance(value, str):
            raise ValueError("Field must be a string")
        return True

class EmailField(CharField):
    def validate(self, value):
        super().validate(value)
        if value is not None and "@" not in value:
            raise ValueError("Invalid email format")
        return True


class PhoneField(ArgumentsField):
    def validate(self, value):
        super().validate(value)
        if value is not None and (not isinstance(value, (str, int)) or not str(value).isdigit() or not str(value).startswith("7") or len(str(value)) != 11):
            raise ValueError("Invalid phone number format")
        return True


class DateField(ArgumentsField):
    def validate(self, value):
        super().validate(value)
        try:
            datetime.datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format, should be DD.MM.YYYY")
        return True


class BirthDayField(DateField):
    def validate(self, value):
        super().validate(value)
        birth_date = datetime.datetime.strptime(value, "%d.%m.%Y")
        if (datetime.datetime.today() - birth_date).days / 365.25 > 70:
            raise ValueError("Age must be less than 70 years")
        return True


class GenderField(ArgumentsField):
    ALLOWED_VALUES = {0, 1, 2}
    
    def validate(self, value):
        super().validate(value)
        if value is not None and value not in self.ALLOWED_VALUES:
            raise ValueError("Gender must be 0, 1, or 2")
        return True

class ClientIDsField(ArgumentsField):
    def validate(self, value):
        super().validate(value)
        if not isinstance(value, list) or not all(isinstance(i, int) for i in value):
            raise ValueError("client_ids must be a list of integers")
        if not value:
            raise ValueError("client_ids cannot be empty")
        return True

class ClientsInterestsRequest(MethodRequest):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)


class OnlineScoreRequest(MethodRequest):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)


class MethodRequest(object):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN
    
    def __init__(self, data):
        self.data = data
        self.context = {}

    def validate(self):
        errors = []
        for field_name, field in self.fields.items():
            value = self.data.get(field_name)
            try:
                field.validate_field(value)
            except ValueError as e:
                errors.append(str(e))
        if errors:
            return {"code": 422, "error": " ".join(errors)}
        return None

    def process_method(self):
        method = self.data['method']
        if method == 'online_score':
            return self.online_score()
        elif method == 'clients_interests':
            return self.clients_interests()
        else:
            return {"code": 422, "error": f"Method '{method}' not found."}

    def online_score(self):
        arguments = self.data['arguments']
        phone = arguments.get('phone')
        email = arguments.get('email')
        first_name = arguments.get('first_name')
        last_name = arguments.get('last_name')
        birthday = arguments.get('birthday')
        gender = arguments.get('gender')

        if not self.validate_fields_for_online_score(phone, email, first_name, last_name, gender, birthday):
            return {"code": 422, "error": "Invalid fields for online_score."}

        score = get_score(self.data['account'], phone, email, birthday, gender, first_name, last_name)
        return {"code": 200, "response": {"score": score}}

    def clients_interests(self):
        arguments = self.data['arguments']
        client_ids = arguments.get('client_ids')
        if not client_ids:
            return {"code": 422, "error": "client_ids must be a non-empty array."}

        interests = {cid: get_interests(self.data['account'], cid) for cid in client_ids}
        return {"code": 200, "response": interests}

    def validate_fields_for_online_score(self, phone, email, first_name, last_name, gender, birthday):
        if not (phone and email) and not (first_name and last_name) and not (gender and birthday):
            return False
        return True


def check_auth(request):
    if request.is_admin:
        digest = hashlib.sha512((datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).encode('utf-8')).hexdigest()
    else:
        digest = hashlib.sha512((request.account + request.login + SALT).encode('utf-8')).hexdigest()
    return digest == request.token


def method_handler(request, ctx, store):
    response, code = None, None
    return response, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = None

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path]({"body": request, "headers": self.headers}, context, self.store)
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r).encode('utf-8'))
        return


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-p", "--port", action="store", type=int, default=8080)
    parser.add_argument("-l", "--log", action="store", default=None)
    args = parser.parse_args()
    logging.basicConfig(filename=args.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", args.port), MainHTTPHandler)
    logging.info("Starting server at %s" % args.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()