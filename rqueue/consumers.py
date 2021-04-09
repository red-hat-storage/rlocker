import json

import random
import time

from channels.generic.websocket import WebsocketConsumer


class WSConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

        for i in range(100):
            self.send(json.dumps({'message':i}))
            self.send(json.dumps({'message':i}))
            self.send(json.dumps({'message':i}))
            self.send(json.dumps({'message':i}))
            self.send(json.dumps({'message':i}))
            self.send(json.dumps({'message':i}))
            self.send(json.dumps({'message':i}))
            self.send(json.dumps({'message':i}))
            time.sleep(5)