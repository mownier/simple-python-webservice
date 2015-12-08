from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
import threading
import argparse
import re
import cgi

class LocalData(object):
    records = {}

class HTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if None != re.search('/api/v1/getrecord/*', self.path):
            recordID = self.path.split('/')[-1]
            print recordID
            if LocalData.records.has_key(recordID):
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(LocalData.records[recordID])
            else :
                self.send_response(400, 'Bad Request: record does not exist')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write('{"message": "Record not found"}')
        else :
            self.send_response(403)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
        return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = True

    def shutdown(self):
        self.socket.close()
        HTTPServer.shutdown(self)

class SimpleHttpServer():
    def __init__(self, ip, port):
        self.server = ThreadedHTTPServer((ip, port), HTTPRequestHandler)

    def start(self):
        self.server_thread = threading.Thread(target = self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def waitForThread(self):
        self.server_thread.join()

    def addRecord(self, recordID, jsonEncodedRecord):
        LocalData.records[recordID] = jsonEncodedRecord

    def stop(self):
        self.server.shutdown()
        self.waitForThread()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'HTTP Server')
    parser.add_argument('port', type = int, help = 'Listening port for HTTP Server')
    parser.add_argument('ip', help = 'HTTP Server IP')
    args = parser.parse_args()

server = SimpleHttpServer(args.ip, args.port)
print 'HTTP Server Running...........'
server.start()
server.waitForThread()
