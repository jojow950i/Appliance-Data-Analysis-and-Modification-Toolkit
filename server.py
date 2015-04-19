import tornado.ioloop
import tornado.web
import tornado.autoreload
from tornado.concurrent import Future
import os
import random
import time
import json
import pandas
import datetime
import uuid
import threading
from tornado import gen
import generate_order
import metadata_import
import yaml


i = 0
redd_path = '/path/to/REDD/'
greend_path = '/path/to/GREEND/'
iAWE_path = '/path/to/iAWE/'
channels = {}

checkboxes = ('REDD', 'GREEND', 'iAWE')

waiters = {}


class Channel:
    def __init__(self, channel_name='', datasets={}):
        self.datasets = datasets
        self.name = channel_name

    @property
    def __repr__(self):
        return self.name, self.datasets


class MainHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self):
        client_id = str(uuid.uuid4())
        global i
        i = 0
        print("Main Get!")
        message = {'id': client_id}
        self.render("index.html", message=message)


class EntryAllHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def post(self):
        toSend = list()

        chosen = []

        for checkbox in checkboxes:
            if self.get_argument(checkbox) == 'true':
                chosen.append(checkbox)


        for c_channel in channels:
            s1 = set(channels[c_channel]['datasets'].keys())
            aus = set(chosen).intersection(s1)
            availability = {'small': 0, 'medium': 0, 'large': 0}

            for a in aus:
                for part in channels[c_channel]['datasets'][a]:
                    availability[part] += len(channels[c_channel]['datasets'][a][part])

            if aus != set([]):
                message = {
                    "id": str(int(time.time() + int(random.random() * 10000))),
                    "name": c_channel,
                    "from": str((int(time.time() * 1000000) >> 9) + int(random.random() * 100000)),
                    "availability": availability,
                    "small": availability['small'],
                    "medium": availability['medium'],
                    "large": availability['large'],
                }

                message["html"] = tornado.escape.to_basestring(self.render_string("entry.html", message=message))

                toSend.append(message)

        self.write(dict({'v': toSend}))


class GenerateOrderHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def post(self):
        self.write('')

        gotten_id = self.get_argument('id', None)
        timeframe = self.get_argument('timeframe', None)
        apps = json.loads(self.get_argument('appliances', None))
        noise = int(self.get_argument('noise', None))
        missing = int(self.get_argument('missing', None))
        calcTotalComplexity = self.get_argument('calcTotalComplexity', None)

        print("starting thread now...")
        order = generate_order.GenerateOrder(gotten_id, timeframe, apps, noise, missing, calcTotalComplexity, waiters,
                                             redd_path, channels)
        c_thread = threading.Thread(target=order.generate, args=())
        c_thread.start()


class StatusBuffer(object):
    def __init__(self):
        self.for_output = []

    def output_status(self, message):
        while len(self.for_output) == 0:
            pass

        for future in self.for_output:
            future.set_result(message)
        self.for_output = []

    def wait_for_output(self):
        result_future = Future()
        self.for_output.append(result_future)
        return result_future


class UpdateStatusHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    @gen.coroutine
    def post(self):
        global waiters
        gotten_id = self.get_argument('id', None)

        last_time = pandas.Timestamp(datetime.datetime.now())

        if gotten_id in waiters.keys():
            waiters[gotten_id]['last_time'] = last_time
        else:
            waiters.update({gotten_id: {'buffer': StatusBuffer(), 'last_time': last_time}})

        buffer = waiters[gotten_id]['buffer']

        future = buffer.wait_for_output()
        status_update = yield future
        self.write({'update': status_update})


class CheckboxesAllHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def post(self):
        to_send = list()

        for checkbox in checkboxes:
            message = {

                "dataset": checkbox,
            }

            message["html"] = tornado.escape.to_basestring(self.render_string("add_checkboxes.html", message=message))

            to_send.append(message)

        self.write(dict({'v': to_send}))


class DownloadHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def post(self, path):
        file = open('download/' + path, 'r')
        print(path)
        self.set_header('Content-Type', 'text/csv')
        self.set_header('Content-Disposition', 'attachment; filename=HouseData.csv')
        self.write(file.read())


application = tornado.web.Application(
    [

        (r"/", MainHandler),
        (r"/entry/all", EntryAllHandler),
        (r"/checkboxes/all", CheckboxesAllHandler),
        (r"/generate", GenerateOrderHandler),
        (r'/update', UpdateStatusHandler),
        (r'/download/(.*)', DownloadHandler),  # tornado.web.StaticFileHandler, {"path": "./download"}),

    ],
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static"),
)

redd_infos = json.load(open("dataset_infos/REDD_infos.json", "r"))
greend_infos = json.load(open("dataset_infos/GREEND_infos.json", "r"))
iawe_infos = json.load(open("dataset_infos/iAWE_infos.json", "r"))


if __name__ == "__main__":
    print("Server Started")


    channels = metadata_import.import_datasets()

    print(channels)
    tornado.autoreload.start(io_loop=None, check_time=500)

    css = os.path.join(os.path.dirname(__file__) + "/static", "index.css")
    js = os.path.join(os.path.dirname(__file__) + "/static", "main.js")
    entry = os.path.join(os.path.dirname(__file__) + "/templates", "entry.html")
    check = os.path.join(os.path.dirname(__file__) + "/templates", "add_checkboxes.html")

    html = os.path.join(os.path.dirname(__file__) + "/templates", "index.html")

    tornado.autoreload.watch(css)
    tornado.autoreload.watch(html)
    tornado.autoreload.watch(js)
    tornado.autoreload.watch(entry)
    tornado.autoreload.watch(check)

    application.listen(9999)
    tornado.ioloop.IOLoop.instance().start()