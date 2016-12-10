from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import urllib.parse
import time

# Currently very limited. Does not serve images. Cannot deal with different mimetypes in the same directory...

paths = {}


def add_path(path_name, handler):
    if callable(path_name):
        paths[path_name] = handler
    else:
        paths[lambda x: x == path_name] = handler


def serve_directory(dir, mimetype="text/html"):
    two_slashes = "/" + dir + "/"
    one_slash = dir + "/"
    add_path(lambda x: x.startswith(two_slashes), StaticDirectoryResponse(two_slashes, one_slash,
                                                                          mimetype=mimetype))


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


class Response:
    def __init__(self, mimetype="text/html", code=200):
        self.mimetype = mimetype
        self.code = code

    def begin(self, handler):
        handler.send_response(self.code)
        self.send_content_type(handler)
        handler.end_headers()

    def end(self, handler):
        handler.wfile.write(b'\n')

    def respond(self, handler, path):
        pass

    def send_content_type(self, handler):
        handler.send_header("Content-Type", self.mimetype)


class StaticResponse(Response):
    def __init__(self, content, mimetype="text/html", code=200):
        super().__init__(mimetype, code)
        self.content = content

    def respond(self, handler, path):
        self.begin(handler)

        handler.wfile.write(self.content.encode('utf-8'))
        self.end(handler)


class FileResponse(StaticResponse):
    def __init__(self, file_path, mimetype="text/html", code=200):
        class Dummy:
            def encode(self, encoding, errors=""):
                with open(file_path) as file:
                    return ''.join(file.readlines()).encode(encoding, errors)
        content = Dummy()
        super().__init__(content, mimetype, code)


class StaticDirectoryResponse(Response):
    def __init__(self, base_path, serve_dir, mimetype="text/html", code=200):
        super().__init__(mimetype, code)
        self.base_path = base_path
        self.serve_dir = serve_dir

    def respond(self, handler, path):
        self.begin(handler)

        try:
            with open(self.serve_dir + path.path[len(self.base_path):]) as serve_file:  # AAAAAAAAAHHHHH
                handler.wfile.write(''.join(serve_file.readlines()).encode('utf-8'))
        except FileNotFoundError as err:
            print("File not found: " + err.filename)

        self.end(handler)


class GeneratorResponse(Response):
    def __init__(self, gen, mimetype="text/event-stream", code=200):
        super().__init__(mimetype, code)
        self.gen = gen

    def respond(self, handler, path):
        self.begin(handler)

        gen = self.gen()  # Evaluate function to get generator object

        try:
            while True:
                resp = gen.__next__()
                handler.wfile.write(resp.encode('utf-8'))
                handler.wfile.flush()
        except StopIteration:
            pass
        finally:
            self.end(handler)


NOT_FOUND_RESPONSE = StaticResponse("404 Not Found", mimetype="text/plain", code=404)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        real_path = parsed_path.path
        for path, response in paths.items():
            if path(real_path):
                try:
                    response.respond(self, parsed_path)
                except BrokenPipeError:
                    pass  # Is okay
                break
        else:
            NOT_FOUND_RESPONSE.respond(self, parsed_path)


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


def run(port=5000, daemon_threads=True):
    server = ThreadedHTTPServer(('localhost', port), Handler)
    server.daemon_threads = daemon_threads
    print('Starting dashboard server on port {}'.format(port))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
        server.server_close()

if __name__ == '__main__':
    print("Testing dashboard-server")

    def gen():
        for i in range(100):
            time.sleep(1)
            yield ServerSentEvent(str(i)).encode()

    add_path("/", FileResponse("templates/evttest.html"))
    add_path("/eventsource", GeneratorResponse(gen))

    run()