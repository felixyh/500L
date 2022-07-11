# Listing Directories

# Serving Static Pages
# serving pages from the disk instead of generating them on the fly. We'll start by rewriting do_GET

from http.server import BaseHTTPRequestHandler, HTTPServer
import os


class ServerException(BaseException):
    pass


class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            # Figure out what exactly is being requested
            full_path = os.getcwd() + self.path

            # If it does not exist...
            if not os.path.exists(full_path):
                raise ServerException("'{0}' not found".format(self.path))

            # If it is a file...
            elif os.path.isfile(full_path):
                self.handle_file(full_path)

            # If it is something we don't handle
            else:
                raise ServerException("Unknown object '{0}'".format(self.path))

        # Handle errors.
        except ServerException as msg:
            self.handle_error(msg)

    def handle_file(self, full_path):
        try:
            with open(full_path, 'rb') as reader:
                content = reader.read()
            self.send_content(content)
        except IOError as msg:
            msg = "'{0}' cannot be read: {1}".format(self.path, msg)
            self.handle_error(msg)

    # handle unknown objects
    Error_Page = """\
        <html>
        <body>
        <h1>Error accessing {path}</h1>
        <p>{msg}</p>
        </body>
        </html>
        """

    def handle_error(self, msg):
        content = self.Error_Page.format(path=self.path, msg=msg)

        # python3 send_content 只能接受字节，需要encode() 把字符串转换成字节
        self.send_content(content.encode(), 404)

    # send actual content
    def send_content(self, content, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


if __name__ == '__main__':
    serverAddress = ('', 8080)
    server = HTTPServer(serverAddress, RequestHandler)
    server.serve_forever()
