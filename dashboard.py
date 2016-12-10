import dashboard_server
from dashboard_server import FileResponse, Response, GeneratorResponse, ServerSentEvent
from queue import Queue
import json

subscriptions = []
graphs = {}

dashboard_server.add_path("/", FileResponse("templates/index.html"))
dashboard_server.serve_directory("js", mimetype="application/javascript")
dashboard_server.serve_directory("images", mimetype="image/png")
dashboard_server.serve_directory("css", mimetype="text/css")


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

dashboard_server.add_path("/events", GeneratorResponse(gen))


def graph(name, callback):
    graphs[name] = callback


def update(time):
    for g, v in graphs.items():
        send_message({"name": g, "time": time, "value": v()}, event="data")


def send_message(data, event=None):
    sse = ServerSentEvent(json.dumps(data), event=event)
    for qq in subscriptions:
        qq.put(sse)