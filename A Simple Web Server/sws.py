# We're now ready to write our first simple web server. The basic idea is simple:
#
# Wait for someone to connect to our server and send an HTTP request;
# parse that request;
# figure out what it's asking for;
# fetch that data (or generate it dynamically);
# format the data as HTML; and
# send it back.

# in Python 3 which moved BaseHTTPServer to http.server.HTTPServer
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests


class RequestHandler(BaseHTTPRequestHandler):
    """ Handle HTTP Requests by returning a fixed 'page' """

    # Page to send back
    Page = '''\
    <html>
        <body>
            <p>Hello, web!</p>
        </body>
    </html>
    '''

    # Handle a Get Request
    def do_Get(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(self.Page)))
        self.end_headers()
        self.wfile.write(self.Page)


if __name__ == '__main__':
    serverAddress = ('', 8080)
    server = HTTPServer(serverAddress, RequestHandler)
    server.serve_forever()


