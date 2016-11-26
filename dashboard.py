from flask import Flask, Response, render_template, send_from_directory, request
from queue import Queue
import json

app = Flask(__name__)
run = app.run

subscriptions = []
graphs = {}


def graph(name, callback):
    graphs[name] = callback


def update(time):
    for g, v in graphs.items():
        send_message({"name": g, "time": time, "value": v()}, event="data")


def send_message(data, event=None):
    sse = ServerSentEvent(json.dumps(data), event=event)
    for qq in subscriptions:
        qq.put(sse)


class ServerSentEvent:
    def __init__(self, data, event=None, id=None):
        self.data = data
        self.event = event
        self.id = id

    def encode(self):
        st = ""
        if self.event is not None:
            st += "event: {}\n".format(self.event)
        st += "data: {}\n".format(self.data)
        if self.id is not None:
            st += "id: {}\n".format(self.id)
        return st + "\n"


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)


@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)


@app.route('/images/<path:path>')
def send_images(path):
    return send_from_directory('images', path)


@app.route("/")
def main():
    return render_template("index.html")


@app.route("/events")
def sse_events():
    def gen():
        q = Queue()
        for g, _ in graphs.items():
            q.put(ServerSentEvent(json.dumps({"action": "make_chart", "name": g}), "action"))
        subscriptions.append(q)
        try:
            while True:
                ev = q.get()
                yield ev.encode()
        except GeneratorExit:
            subscriptions.remove(q)
            print("Dropped a stream")
    return Response(gen(), mimetype="text/event-stream")
