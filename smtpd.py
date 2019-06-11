#!/usr/bin/env python3

import argparse
from datetime import datetime
import json
import os
import sys
import time
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
            file_name = os.path.join('messages', str(uuid.uuid4().hex))
            with open(file_name, 'w') as open_file:
                content = envelope.original_content.decode('utf-8').replace("\r\r\n", "\r\n")
                message = mailparser.parse_from_string(content)
                json.dump({'mail_from': envelope.mail_from,
                           'rcpt_tos': envelope.rcpt_tos,
                           'subject': message.subject,
                           'body': message.body,
                           'data': content,
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
        pid = str(os.getpid())
        pidfile = "/run/postoffice/postoffice.pid"
        open(pidfile, 'w').write(pid)
        print("Running smtpd server on {}:{}\n".format(args.host, args.port))
        while True:
            time.sleep(3)
    except Exception as exc:
        print(exc, file=sys.stderr)
        controller.stop()
    finally:
        os.unlink(pidfile)
