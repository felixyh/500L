# We're now ready to write our first simple web server. The basic idea is simple:
#
# Wait for someone to connect to our server and send an HTTP request;
# parse that request;
# figure out what it's asking for;
# fetch that data (or generate it dynamically);
# format the data as HTML; and
# send it back.

# in Python 3 which moved BaseHTTPServer to http.server.HTTPServer

import http.server as h


class RequestHandler(h.BaseHTTPRequestHandler):
    """ Handle HTTP Requests by returning a fixed 'page' """

    # Page to send back
    Page = '''\
    <html>
        <body>
            <p>Hello, web!</p>
        </body>
    </html>
    '''

    # Handle a Get Request, 重写do_GET() 方法
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(self.Page)))
        self.end_headers()
        # encode 把字符串转换成字节
        self.wfile.write(self.Page.encode())

# ----------------------------------------------------------------------


if __name__ == '__main__':
    serverAddress = ('', 8080)
    server = h.HTTPServer(serverAddress, RequestHandler)
    server.serve_forever()


