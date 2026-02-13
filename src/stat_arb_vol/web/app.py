"""Minimal web dashboard for visualizing latest backtest artifacts."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path("reports").resolve()


class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        if self.path in ["/", "/index.html"]:
            self._serve_index()
        elif self.path == "/equity.png":
            self._serve_binary(ROOT / "equity_curve.png", "image/png")
        elif self.path == "/report.md":
            self._serve_binary(ROOT / "performance_report.md", "text/markdown; charset=utf-8")
        else:
            self.send_error(404, "Not found")

    def _serve_index(self) -> None:
        html = """
<!DOCTYPE html>
<html lang=\"en\">
<head><meta charset=\"UTF-8\"><title>Stat Arb Dashboard</title></head>
<body style=\"font-family:Arial;margin:2rem;\">
    <h1>Statistical Arbitrage & Volatility Strategy</h1>
    <p>Generated from mock-or-real crypto data.</p>
    <h2>Equity Curve</h2>
    <img src=\"/equity.png\" style=\"max-width:900px;width:100%;border:1px solid #ddd;\"/>
    <h2>Performance Report</h2>
    <p><a href=\"/report.md\">Open Markdown report</a></p>
</body>
</html>
"""
        data = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _serve_binary(self, path: Path, ctype: str) -> None:
        if not path.exists():
            self.send_error(404, f"Missing artifact: {path.name}")
            return
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def run_dashboard(port: int = 8000) -> None:
    server = HTTPServer(("0.0.0.0", port), DashboardHandler)
    print(f"Dashboard available at http://localhost:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_dashboard()
