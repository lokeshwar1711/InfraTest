"""Local HTTP and TCP smoke-test servers for manual InfraTest verification."""

from __future__ import annotations

import json
import socketserver
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


HTTP_HOST = "127.0.0.1"
HTTP_PORT = 8765
TCP_HOST = "127.0.0.1"
TCP_PORT = 8766


class HealthHandler(BaseHTTPRequestHandler):
    """Simple health endpoint for manual InfraTest runs."""

    def do_GET(self) -> None:  # noqa: N802
        if self.path != "/health":
            self.send_response(404)
            self.end_headers()
            return

        payload = {
            "status": "healthy",
            "service": "manual-smoke-server",
        }
        body = json.dumps(payload).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return


class TCPHandler(socketserver.BaseRequestHandler):
    """Accept connections and close immediately."""

    def handle(self) -> None:
        self.request.sendall(b"InfraTest smoke server\n")


def main() -> None:
    http_server = ThreadingHTTPServer((HTTP_HOST, HTTP_PORT), HealthHandler)
    tcp_server = socketserver.ThreadingTCPServer((TCP_HOST, TCP_PORT), TCPHandler)

    print(f"HTTP smoke server listening on http://{HTTP_HOST}:{HTTP_PORT}/health")
    print(f"TCP smoke server listening on {TCP_HOST}:{TCP_PORT}")
    print("Press Ctrl+C to stop both servers.")

    http_thread = threading.Thread(target=http_server.serve_forever, daemon=True)
    tcp_thread = threading.Thread(target=tcp_server.serve_forever, daemon=True)
    http_thread.start()
    tcp_thread.start()

    try:
        http_thread.join()
        tcp_thread.join()
    except KeyboardInterrupt:
        print("\nStopping smoke servers...")
    finally:
        http_server.shutdown()
        tcp_server.shutdown()
        http_server.server_close()
        tcp_server.server_close()


if __name__ == "__main__":
    main()