# Serving Static Pages
# serving pages from the disk instead of generating them on the fly. We'll start by rewriting do_GET

from http.server import BaseHTTPRequestHandler
import os


class ServerException:
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
        except Exception as msg:
            self.handle_error(msg)

    def handle_error(self, msg):
        pass



