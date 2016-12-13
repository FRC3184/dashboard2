import dashboard_server
from dashboard_server import FileResponse, Response, GeneratorResponse, ServerSentEvent
from queue import Queue
import json

subscriptions = []
graphs = {}
choosers = {}
chooser_status = {}

dashboard_server.serve_path("/", FileResponse("templates/index.html"))
dashboard_server.serve_directory("js", mimetype="application/javascript")
dashboard_server.serve_directory("images", mimetype="image/png")
dashboard_server.serve_directory("css", mimetype="text/css")


def gen():
    q = Queue()
    for g, _ in graphs.items():
        q.put(ServerSentEvent(json.dumps({"action": "make_chart", "name": g}), "action"))
    for name, opts in choosers.items():
        q.put(ServerSentEvent(json.dumps({"action": "make_chooser", "name": name, "options": opts}), "action"))
    subscriptions.append(q)
    try:
        while True:
            ev = q.get()
            yield ev.encode()
    except GeneratorExit:
        subscriptions.remove(q)
        print("Dropped a stream")

dashboard_server.serve_path("/events", GeneratorResponse(gen))


def update_chooser(handler, path, data):
    data = json.loads(data.decode("U8"))
    chooser_status[data['name']] = data['option']
    return 200

dashboard_server.method_path("/update_chooser", update_chooser)


def graph(name, callback):
    graphs[name] = callback


def chooser(name, options):
    choosers[name] = options
    chooser_status[name] = None


def get_chooser(name):
    return chooser_status[name]


def update(time):
    for g, v in graphs.items():
        send_message({"name": g, "time": time, "value": v()}, event="data")


def send_message(data, event=None):
    sse = ServerSentEvent(json.dumps(data), event=event)
    for qq in subscriptions:
        qq.put(sse)
