import ssl
import socketserver
from http.server import BaseHTTPRequestHandler
import threading

class httpHandler(BaseHTTPRequestHandler):
  
    def do_GET(self):
        ## Second get is Favicon
        if not hasattr(self, 'user_agent'):
            
            ua = self.headers.get('User-Agent')
            if 'Windows' in ua:
                self.user_agent = "windows"
                serve_redirect(self, self.server)
                return

            elif 'iPhone' in ua:
                self.user_agent = "ios"

        if self.path == "/localhost.pem":
            serve_redirect(self, self.server)
                
        with open("localhost.pem", "rb") as file:
            pem = file.read()
            file.close()

        self.send_response(302)
        self.send_header("Location", "/localhost.pem")
        self.send_header("Content-type", "text/html; charset=%s" % 'utf8')
        self.send_header("Content-Length", str(len(pem)))
        self.end_headers()
        self.wfile.write(pem)

        

class httpsHandler(httpHandler):
    def do_GET(self):
        resource = self.path
        if not resource == "/":
            self.send_response(404)
            self.end_headers()

        with open("index.html", "rb") as file:
            index = file.read()
            file.close()

        self.send_response(200)

        self.send_header("Content-type", "text/html; charset=%s" % 'utf8')
        self.send_header("Content-Length", str(len(index)))
        self.end_headers()
        self.wfile.write(index)

    def do_POST(self):
        print(self.request.recv(1024))
    
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

def parse_user_agent(string):
    ua = {}
    index = 0
    while index != 0:
        start = string.find("(", index)
        index = string.find(")", start)
        info = string[start:index]
        if hasattr(ua, 'system'):
            ua['platform-details'] = info
            continue
        ua['system'] = info

def serve_redirect(self, httpd):
        page = """
<!DOCTYPE html>
<html>
    <body>
        <h1>Redirecting..</h1>
    </body>
</html>
""".encode()
        self.send_response(302)
        self.send_header("Content-type", "text/html; charset=utf8")
        self.send_header("Content-Length", str(len(page)))
        self.send_header('Location', 'https://172.20.10.2:8001')
        self.end_headers()
        self.wfile.write(page)

##        httpd.shutdown()

        upgrade()


def upgrade():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ##context.minimum_version = ssl.TLSVersion.TLSv1_3
    ##context.maximum_version = ssl.TLSVersion.TLSv1_3
    context.check_hostname = False
    context.load_cert_chain("localhost.pem", "localhost-key.pem")
    serv_address = ('172.20.10.2', 8001)
    https_daemon = ThreadedTCPServer(serv_address, httpsHandler)
    https_daemon.socket = context.wrap_socket(https_daemon.socket, server_side=True)
    https_daemon.serve_forever()


serv_address = ('172.20.10.2', 8000)
http_daemon = ThreadedTCPServer(serv_address, httpHandler)
http_daemon.allow_reuse_address = True
http_daemon.allow_reuse_port = True

http_daemon.serve_forever()
