import os
import ssl
import sys
import shutil
import pathlib
from http import HTTPStatus
from urllib.parse import urlparse
from urllib.parse import parse_qs
from afd import check_file, delete_tmp_file
from http.server import BaseHTTPRequestHandler, HTTPServer

hostName = sys.argv[1]
serverPort = int(sys.argv[2])
protocol = sys.argv[3]
counter = 2  # because certutil always do two request
_path = str(pathlib.Path(__file__).parent.resolve())
PATH = pathlib.Path(_path)

def generate_selfsigned_cert():
    try:
        OpenSslCommand = 'openssl req -newkey rsa:4096 -x509 -sha256 -days 3650 -nodes -out '+str(PATH/'cert.pem')+' -keyout '+str(PATH/'key.pem')+' -subj "/C=IN/ST=1/L=2/O=3/OU=4 Department/CN=5"'
        os.system(OpenSslCommand)
        print('Certificate Generated')
    except:
        print('Error while generating certificate')
        exit()

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        global counter
        if self.path.split('?')[0] == '/transfer':
            query_components = parse_qs(urlparse(self.path).query)
            if "file" in query_components:
                file = query_components["file"][0]
                _path_file = check_file(file)
                if _path_file != False:
                    try:
                        f = open(_path_file, 'rb')
                    except OSError:
                        self.send_error(HTTPStatus.NOT_FOUND, "Not found")
                        raise KeyboardInterrupt
                    try:
                        fs = os.fstat(f.fileno())
                        self.send_response(HTTPStatus.OK)
                        self.send_header("Content-type", "text/html")
                        self.send_header("Content-Length", str(fs[6]))
                        self.end_headers()

                        shutil.copyfileobj(f, self.wfile)
                    except:
                        self.send_error(HTTPStatus.NOT_FOUND,"Not found")
                    finally:
                        f.close()
                else:
                    self.send_error(HTTPStatus.NOT_FOUND,"Not found")
        counter -= 1
        if counter == 0 or (self.headers['User-Agent'] != "CertUtil URL Agent" and "Microsoft-CryptoAPI" not in self.headers['User-Agent']):
            try:
                delete_tmp_file(file)
            except:
                pass
            finally:
                raise KeyboardInterrupt

if __name__ == "__main__":
    if protocol != "http" and protocol != "https":
        print("Invalid web protocol")
        exit()
    webServer = HTTPServer((hostName, serverPort), MyServer)
    if protocol == "https":
        generate_selfsigned_cert()
        sslwebServer = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        sslwebServer.check_hostname = False
        sslwebServer.load_cert_chain(certfile=PATH/"cert.pem", keyfile=PATH/"key.pem")
        webServer.socket = sslwebServer.wrap_socket(webServer.socket, server_side=True)
    try:
        print("Server started "+protocol+"://%s:%s" % (hostName, serverPort))
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
