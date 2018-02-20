#!/usr/bin/env python3

from datetime import datetime
import json
import uuid
import os


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


with open(os.path.join('messages', str(uuid.uuid4().hex)), 'w') as open_file:
    json.dump({'mail_from': 'test@example.com',
               'rcpt_tos': 'person@example.com',
               'message': 'This is an email message!',
               'timestamp': datetime.utcnow().isoformat()},
              open_file,
              cls=DateTimeEncoder)
