# Listing Directories

# Serving Static Pages
# serving pages from the disk instead of generating them on the fly. We'll start by rewriting do_GET

from http.server import BaseHTTPRequestHandler, HTTPServer
import os


class ServerException(BaseException):
    pass


class CaseNoFile:
    '''File or directory does not exist.'''
    def test(self, handler):
        return not os.path.exists(handler.full_path)

    def act(self, handler):
        raise ServerException("'{0}' not found".format(handler.path))


class CaseExistingFile:
    """File exists."""

    def test(self, handler):
        return os.path.isfile(handler.full_path)

    def act(self, handler):
        handler.handle_file(handler.full_path)


class CaseAlwaysFail:
    """Base case if nothing else worked."""

    def test(self, handler):
        return True

    def act(self, handler):
        raise ServerException("Unknown object '{0}'".format(handler.path))


class CaseDirectoryIndexFile:
    """Serve index.html page for a directory."""

    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')

    def test(self, handler):
        return os.path.isdir(handler.full_path) and \
               os.path.isfile(self.index_path(handler))

    def act(self, handler):
        handler.handle_file(self.index_path(handler))


class CaseDirectoryNoIndexFile:
    """Serve listing for a directory without an index.html page."""

    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')

    def test(self, handler):
        return os.path.isdir(handler.full_path) and \
               not os.path.isfile(self.index_path(handler))

    def act(self, handler):
        handler.list_dir(handler.full_path)


class RequestHandler(BaseHTTPRequestHandler):

    """
    If the requested path maps to a file, that file is served.
    If anything goes wrong, an error page is constructed.
    """

    # modify original code, to remove '()'

    Cases = [CaseNoFile,
             CaseExistingFile,
             CaseDirectoryIndexFile,
             CaseDirectoryNoIndexFile,
             CaseAlwaysFail]

    def do_GET(self):
        try:
            # Figure out what exactly is being requested
            self.full_path = os.getcwd() + self.path

            for case in self.Cases:
                handler = case()
                # below 'self' meant to RequestHandler object, rather than handler=case()
                if handler.test(self):
                    handler.act(self)
                    break

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

    # How to display a directory listing.
    Listing_Page = '''\
        <html>
        <body>
        <ul>
        {0}
        </ul>
        
            <table>
            <tr>  <td>Header</td>         <td>Value</td>          </tr>
            <tr>  <td>Date and time</td>  <td>{date_time}</td>    </tr>
            <tr>  <td>Client host</td>    <td>{client_host}</td>  </tr>
            <tr>  <td>Client port</td>    <td>{client_port}s</td> </tr>
            <tr>  <td>Command</td>        <td>{command}</td>      </tr>
            <tr>  <td>Path</td>           <td>{path}</td>         </tr>
            </table>
        </body>
        </html>
        '''

    def list_dir(self, full_path):
        try:
            entries = os.listdir(full_path)
            bullets = ['<li>{0}</li>'.format(e) for e in entries if not e.startswith('.')]
            values = {
                'date_time': self.date_time_string(),
                'client_host': self.client_address[0],
                'client_port': self.client_address[1],
                'command': self.command,
                'path': self.path
            }
            page = self.Listing_Page.format('\n'.join(bullets), **values)
            self.send_content(page.encode())
        except OSError as msg:
            msg = "'{0}' cannot be listed: {1}".format(self.path, msg)
            self.handle_error(msg)


if __name__ == '__main__':
    serverAddress = ('', 8080)
    server = HTTPServer(serverAddress, RequestHandler)
    server.serve_forever()
