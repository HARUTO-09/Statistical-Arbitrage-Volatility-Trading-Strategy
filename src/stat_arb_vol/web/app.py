"""Interactive web dashboard for visualizing latest backtest artifacts."""

from __future__ import annotations

import json
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
        elif self.path == "/summary.json":
            self._serve_binary(ROOT / "summary.json", "application/json; charset=utf-8")
        else:
            self.send_error(404, "Not found")

    def _serve_index(self) -> None:
        html = """
<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>Stat Arb Dashboard</title>
  <style>
    :root {
      --bg: #0b1020;
      --card: #151d33;
      --muted: #9fb0d0;
      --text: #f0f5ff;
      --accent: #57a6ff;
      --good: #2ac17f;
      --warn: #f2b84b;
      --border: #293654;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
      background: radial-gradient(circle at top right, #1b2c50 0%, var(--bg) 45%);
      color: var(--text);
      min-height: 100vh;
    }
    .container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 2rem 1.2rem 3rem;
    }
    .hero {
      border: 1px solid var(--border);
      background: rgba(10, 16, 32, 0.75);
      border-radius: 16px;
      padding: 1.25rem 1.5rem;
      display: flex;
      justify-content: space-between;
      gap: 1rem;
      flex-wrap: wrap;
      margin-bottom: 1.25rem;
    }
    .hero h1 {
      margin: 0;
      font-size: clamp(1.25rem, 2.5vw, 2rem);
    }
    .hero p {
      margin: 0.4rem 0 0;
      color: var(--muted);
    }
    .pair-chip {
      border: 1px solid var(--border);
      border-radius: 999px;
      padding: 0.45rem 0.85rem;
      font-size: 0.9rem;
      background: rgba(87, 166, 255, 0.12);
      color: #d9e9ff;
      white-space: nowrap;
      align-self: start;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
      gap: 0.8rem;
      margin-bottom: 1.2rem;
    }
    .card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 0.9rem;
    }
    .metric-label {
      color: var(--muted);
      font-size: 0.84rem;
      margin-bottom: 0.35rem;
    }
    .metric-value {
      font-size: 1.15rem;
      font-weight: 700;
      letter-spacing: 0.01em;
    }
    .pill { font-size: 0.78rem; padding: 0.15rem 0.5rem; border-radius: 999px; }
    .pill.good { color: #052212; background: var(--good); }
    .pill.warn { color: #2a1900; background: var(--warn); }

    .panel {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 1rem;
      margin-bottom: 1rem;
    }
    .panel h2 {
      margin: 0 0 0.75rem;
      font-size: 1.1rem;
    }
    .panel img {
      width: 100%;
      border-radius: 10px;
      border: 1px solid var(--border);
      background: #fff;
    }
    .links a {
      color: #9dd0ff;
      text-decoration: none;
      margin-right: 1rem;
    }
    .links a:hover { text-decoration: underline; }
    pre {
      margin: 0;
      white-space: pre-wrap;
      line-height: 1.4;
      color: #d7e3ff;
      font-size: 0.88rem;
    }
  </style>
</head>
<body>
  <main class=\"container\">
    <section class=\"hero\">
      <div>
        <h1>Statistical Arbitrage Control Center</h1>
        <p>Interactive snapshot of the latest backtest run for internship-grade presentation.</p>
      </div>
      <div class=\"pair-chip\" id=\"pair-chip\">Pair: Loading...</div>
    </section>

    <section class=\"grid\" id=\"metrics-grid\"></section>

    <section class=\"panel\">
      <h2>Equity Curve</h2>
      <img src=\"/equity.png\" alt=\"Portfolio Equity Curve\" />
    </section>

    <section class=\"panel\">
      <h2>Artifacts</h2>
      <div class=\"links\">
        <a href=\"/report.md\" target=\"_blank\">Open markdown report</a>
        <a href=\"/summary.json\" target=\"_blank\">Open raw summary JSON</a>
      </div>
    </section>

    <section class=\"panel\">
      <h2>Summary Payload</h2>
      <pre id=\"summary-dump\">Loading...</pre>
    </section>
  </main>

  <script>
    const formatMetric = (key, value) => {
      if (typeof value !== 'number') return String(value);
      const lowered = key.toLowerCase();
      if (lowered.includes('drawdown') || lowered.includes('rate') || lowered.includes('cagr')) {
        return `${(value * 100).toFixed(2)}%`;
      }
      return value.toFixed(3);
    };

    fetch('/summary.json')
      .then((r) => r.ok ? r.json() : Promise.reject(new Error('summary not found')))
      .then((summary) => {
        const pairChip = document.getElementById('pair-chip');
        pairChip.textContent = `Pair: ${summary.selected_pair.join(' / ')}`;

        const metricsGrid = document.getElementById('metrics-grid');
        Object.entries(summary.metrics || {}).forEach(([key, value]) => {
          const card = document.createElement('article');
          card.className = 'card';
          card.innerHTML = `<div class=\"metric-label\">${key}</div><div class=\"metric-value\">${formatMetric(key, value)}</div>`;
          metricsGrid.appendChild(card);
        });

        const targetCard = document.createElement('article');
        const targetStatus = summary.target_achieved
          ? '<span class="pill good">Target achieved</span>'
          : '<span class="pill warn">Below target</span>';
        targetCard.className = 'card';
        targetCard.innerHTML = `
          <div class=\"metric-label\">Sharpe Objective</div>
          <div class=\"metric-value\">${summary.target_sharpe_ratio.toFixed(2)}</div>
          <div style=\"margin-top:0.35rem\">${targetStatus}</div>
        `;
        metricsGrid.appendChild(targetCard);

        document.getElementById('summary-dump').textContent = JSON.stringify(summary, null, 2);
      })
      .catch((error) => {
        document.getElementById('summary-dump').textContent = `Could not load summary.json: ${error.message}`;
      });
  </script>
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
        if ctype.startswith("application/json"):
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                self.send_error(500, "Invalid JSON artifact")
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
