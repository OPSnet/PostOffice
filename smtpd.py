#!/usr/bin/env python3

from datetime import datetime
import json
import os
import uuid

from aiosmtpd.controller import Controller

HOST = '127.0.0.1'
PORT = 10025
DATA_PATH = 'messages'


class Handler(object):
    # noinspection PyPep8Naming,PyMethodMayBeStatic
    async def handle_DATA(self, _, session, envelope):
        # noinspection PyBroadException
        try:
            with open(os.path.join('messages', str(uuid.uuid4().hex)), 'w') as open_file:
                json.dump({'mail_from': envelope.mail_from,
                           'rcpt_tos': envelope.rcpt_tos,
                           'message': envelope.content.decode('utf-8'),
                           'timestamp': datetime.utcnow().isoformat()},
                          open_file)
            return '250 OK'
        except Exception:
            return '500 Could not process your message'


if __name__ == '__main__':
    handler = Handler()
    controller = Controller(handler, hostname='127.0.0.1', port=10025)
    # noinspection PyBroadException
    try:
        controller.start()
        input('Running smtpd server on {}:{}'.format(HOST, PORT))
    except Exception:
        controller.stop()
