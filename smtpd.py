#!/usr/bin/env python3

import argparse
from datetime import datetime
import json
import os
import uuid

from aiosmtpd.controller import Controller
import mailparser

DATA_PATH = 'messages'


class Handler(object):
    # noinspection PyPep8Naming,PyMethodMayBeStatic
    async def handle_DATA(self, _, session, envelope):
        print('Recieved message...')
        # noinspection PyBroadException
        try:
            with open(os.path.join('messages', str(uuid.uuid4().hex)), 'w') as open_file:
                message = mailparser.parse_from_string(envelope.content.decode('utf-8'))
                json.dump({'mail_from': envelope.mail_from,
                           'rcpt_tos': envelope.rcpt_tos,
                           'subject': message.subject,
                           'body': message.body,
                           'data': envelope.content.decode('utf-8'),
                           'timestamp': datetime.utcnow().isoformat()},
                          open_file)
            return '250 OK'
        except Exception:
            return '500 Could not process your message'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('host', type=str)
    parser.add_argument('port', type=int)
    args = parser.parse_args()
    handler = Handler()
    controller = Controller(handler, hostname=args.host, port=args.port)
    # noinspection PyBroadException
    try:
        controller.start()
        input("Running smtpd server on {}:{}\n".format(args.host, args.port))
    except Exception:
        controller.stop()
