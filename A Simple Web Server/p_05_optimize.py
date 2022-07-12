# The CGI Protocol

from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import subprocess


class ServerException(BaseException):
    pass


class BaseCase(object):
    """Parent for case handlers."""

    def handle_file(self, handler, full_path):
        try:
            with open(full_path, 'rb') as reader:
                content = reader.read()
            handler.send_content(content)
        except IOError as msg:
            msg = "'{0}' cannot be read: {1}".format(full_path, msg)
            handler.handle_error(msg)

    def run_cgi(self, handler):
        # modify the original code, as the path includes some special characters,
        # as a workaround, chdir to the path and run it

        file_name = os.path.basename(handler.full_path)
        dir_name = os.path.dirname(handler.full_path)
        cmd = "python3 " + file_name
        os.chdir(dir_name)

        # change the original code,
        # use subprocess.Popen rather than os.Popen which has been revoked already.
        res = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE)
        res.stdin.close()
        # res.stdout.read() output in bytes, so no need to do encoding of str anymore
        stdoutput = res.stdout.read()
        res.stdout.close()
        handler.send_content(stdoutput)

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

    def list_dir(self, handler):
        try:
            entries = os.listdir(handler.full_path)
            bullets = ['<li>{0}</li>'.format(e) for e in entries if not e.startswith('.')]
            values = {
                'date_time': handler.date_time_string(),
                'client_host': handler.client_address[0],
                'client_port': handler.client_address[1],
                'command': handler.command,
                'path': handler.path
            }
            page = self.Listing_Page.format('\n'.join(bullets), **values)
            handler.send_content(page.encode())
        except OSError as msg:
            msg = "'{0}' cannot be listed: {1}".format(handler.path, msg)
            handler.handle_error(msg)

    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')

    def test(self, handler):
        assert False, 'Not implemented.'

    def act(self, handler):
        assert False, 'Not implemented.'


class CaseCGIHandler(BaseCase):
    def test(self, handler):
        return os.path.isfile(handler.full_path) and \
            handler.full_path.endswith('.py')

    def act(self, handler):
        self.run_cgi(handler)


class CaseNoFile(BaseCase):
    """File or directory does not exist."""
    def test(self, handler):
        return not os.path.exists(handler.full_path)

    def act(self, handler):
        raise ServerException("'{0}' not found".format(handler.path))


class CaseExistingFile(BaseCase):
    """File exists."""

    def test(self, handler):
        return os.path.isfile(handler.full_path)

    def act(self, handler):
        self.handle_file(handler, handler.full_path)


class CaseAlwaysFail(BaseCase):
    """Base case if nothing else worked."""

    def test(self, handler):
        return True

    def act(self, handler):
        raise ServerException("Unknown object '{0}'".format(handler.path))


class CaseDirectoryIndexFile(BaseCase):
    """Serve index.html page for a directory."""

    def test(self, handler):
        return os.path.isdir(handler.full_path) and \
               os.path.isfile(self.index_path(handler))

    def act(self, handler):
        self.handle_file(handler, self.index_path(handler))


class CaseDirectoryNoIndexFile(BaseCase):
    """Serve listing for a directory without an index.html page."""

    def test(self, handler):
        return os.path.isdir(handler.full_path) and \
               not os.path.isfile(self.index_path(handler))

    def act(self, handler):
        self.list_dir(handler)


class RequestHandler(BaseHTTPRequestHandler):
    """
    If the requested path maps to a file, that file is served.
    If anything goes wrong, an error page is constructed.
    """

    # modify original code, to remove '()'

    Cases = [CaseCGIHandler,
             CaseNoFile,
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
