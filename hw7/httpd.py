from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import unquote
from datetime import datetime
import os
import argparse
import mimetypes

class SimpleHandler(BaseHTTPRequestHandler):
    server_version = "CustomHTTP/0.1"
    document_root = "."  # будет установлено из аргумента -r

    def do_GET(self):
        self.handle_get_head()

    def do_HEAD(self):
        self.handle_get_head(head_only=True)

    def handle_get_head(self, head_only=False):
        path = unquote(self.path)
        clean_path = path.lstrip("/")
        full_path = os.path.join(self.document_root, clean_path)

        if os.path.isdir(full_path):  # если путь — директория
            full_path = os.path.join(full_path, "index.html")

        if not os.path.exists(full_path) or not os.path.isfile(full_path):
            self.send_response(404)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Connection", "close")
            self.end_headers()
            if not head_only:
                self.wfile.write(b'Not found\n')
            return

        content_type, _ = mimetypes.guess_type(full_path)
        if content_type is None:
            content_type = "application/octet-stream"

        content_length = os.path.getsize(full_path)
        self.send_response(200)
        self.send_header("Date", self.date_time_string())
        self.send_header("Server", self.server_version)
        self.send_header("Content-Length", str(content_length))
        self.send_header("Content-Type", content_type)
        self.send_header("Connection", "close")
        self.end_headers()

        if not head_only:
            with open(full_path, "rb") as f:
                self.wfile.write(f.read())

        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Connection", "close")
        self.end_headers()
            
        # Отправляем тело ответа
        self.wfile.write(body)

    def method_not_allowed(self):
        self.send_response(405)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(b'Method Not Allowed\n')
    # Обработка всех остальных методов — 405
    
    def do_POST(self): self.method_not_allowed()
    def do_PUT(self): self.method_not_allowed()
    def do_DELETE(self): self.method_not_allowed()
    def do_PATCH(self): self.method_not_allowed()
    def do_OPTIONS(self): self.method_not_allowed()
    
def parse_args():
    parser = argparse.ArgumentParser(description="Simple HTTP server with -r and -w")
    parser.add_argument("-r", "--root", default=".", help="Document root (default: current directory)")
    parser.add_argument("-w", "--workers", type=int, default=1, help="Number of worker processes (default: 1)")
    parser.add_argument("-p", "--port", type=int, default=8000, help="Port to listen on (default: 8000)")
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    SimpleHandler.document_root = args.root

    print(f"Serving on http://localhost:{args.port}")
    print(f"DOCUMENT_ROOT: {args.root}")
    print(f"Workers: {args.workers} (not used yet)")

    server = HTTPServer(('localhost', args.port), SimpleHandler)
    server.serve_forever()
