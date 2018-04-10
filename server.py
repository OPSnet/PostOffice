#!/usr/bin/env python3

import json
import os
import falcon


DATA_PATH = 'messages'


class Resource(object):
    # noinspection PyMethodMayBeStatic
    def on_get(self, _, resp):
        response = []
        for entry in os.scandir(DATA_PATH):
            if entry.name == '.gitkeep':
                continue
            with open(entry.path) as open_file:
                try:
                    response.append(json.load(open_file))
                except json.decoder.JSONDecodeError:
                    pass
            os.remove(entry.path)
        resp.body = str.encode(json.dumps(response))
        resp.status = falcon.HTTP_200


application = falcon.API()
application.add_route('/', Resource())
