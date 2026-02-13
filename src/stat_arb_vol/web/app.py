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
  <title>Quantitative Trading Analytics</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    :root {
      --bg-primary: #0a0e1a;
      --bg-secondary: #0f1419;
      --bg-tertiary: #151b26;
      --surface: rgba(21, 27, 38, 0.6);
      --surface-hover: rgba(30, 40, 55, 0.8);
      --border: rgba(60, 80, 110, 0.3);
      --border-hover: rgba(80, 120, 160, 0.5);
      --text-primary: #f0f6ff;
      --text-secondary: #a0b0d0;
      --text-muted: #6b7a96;
      --accent-blue: #3b9eff;
      --accent-cyan: #00d4ff;
      --success: #10b981;
      --success-bg: rgba(16, 185, 129, 0.12);
      --warning: #f59e0b;
      --warning-bg: rgba(245, 158, 11, 0.12);
      --danger: #ef4444;
      --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.2);
      --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.3);
      --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.4);
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: linear-gradient(135deg, #0a0e1a 0%, #151b26 50%, #0f1419 100%);
      color: var(--text-primary);
      min-height: 100vh;
      overflow-x: hidden;
      position: relative;
    }

    body::before {
      content: '';
      position: fixed;
      top: -50%;
      right: -50%;
      width: 100%;
      height: 100%;
      background: radial-gradient(circle, rgba(59, 158, 255, 0.08) 0%, transparent 70%);
      animation: float 20s ease-in-out infinite;
      pointer-events: none;
    }

    @keyframes float {
      0%, 100% { transform: translate(0, 0) rotate(0deg); }
      50% { transform: translate(-30px, 30px) rotate(180deg); }
    }

    .container {
      max-width: 1400px;
      margin: 0 auto;
      padding: 2rem 1.5rem 4rem;
      position: relative;
      z-index: 1;
    }

    .header {
      margin-bottom: 2.5rem;
      animation: slideDown 0.6s ease-out;
    }

    @keyframes slideDown {
      from {
        opacity: 0;
        transform: translateY(-20px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    .title-section {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      flex-wrap: wrap;
      gap: 1.5rem;
      margin-bottom: 1rem;
    }

    .title-wrapper h1 {
      font-size: clamp(1.75rem, 4vw, 2.5rem);
      font-weight: 700;
      background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-blue) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      margin-bottom: 0.5rem;
      letter-spacing: -0.02em;
    }

    .subtitle {
      color: var(--text-secondary);
      font-size: 1rem;
      font-weight: 500;
    }

    .status-badge {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.75rem 1.25rem;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      backdrop-filter: blur(12px);
      font-weight: 600;
      transition: all 0.3s ease;
    }

    .status-badge:hover {
      background: var(--surface-hover);
      border-color: var(--border-hover);
      transform: translateY(-2px);
      box-shadow: var(--shadow-md);
    }

    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--success);
      animation: pulse 2s ease-in-out infinite;
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.6; transform: scale(1.2); }
    }

    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 1.25rem;
      margin-bottom: 2rem;
      animation: fadeInUp 0.8s ease-out 0.2s both;
    }

    @keyframes fadeInUp {
      from {
        opacity: 0;
        transform: translateY(30px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    .metric-card {
      position: relative;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 1.5rem;
      backdrop-filter: blur(12px);
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      overflow: hidden;
      cursor: pointer;
    }

    .metric-card::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan));
      opacity: 0;
      transition: opacity 0.3s ease;
    }

    .metric-card:hover {
      background: var(--surface-hover);
      border-color: var(--border-hover);
      transform: translateY(-4px);
      box-shadow: var(--shadow-lg);
    }

    .metric-card:hover::before {
      opacity: 1;
    }

    .metric-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.75rem;
    }

    .metric-label {
      color: var(--text-secondary);
      font-size: 0.875rem;
      font-weight: 500;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .metric-icon {
      width: 32px;
      height: 32px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.25rem;
      background: rgba(59, 158, 255, 0.1);
      color: var(--accent-blue);
    }

    .metric-value {
      font-size: 2rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      margin-bottom: 0.5rem;
      font-variant-numeric: tabular-nums;
    }

    .metric-change {
      display: inline-flex;
      align-items: center;
      gap: 0.25rem;
      font-size: 0.875rem;
      padding: 0.25rem 0.5rem;
      border-radius: 6px;
      font-weight: 500;
    }

    .metric-change.positive {
      color: var(--success);
      background: var(--success-bg);
    }

    .metric-change.negative {
      color: var(--warning);
      background: var(--warning-bg);
    }

    .progress-bar {
      width: 100%;
      height: 6px;
      background: rgba(59, 158, 255, 0.1);
      border-radius: 3px;
      overflow: hidden;
      margin-top: 0.75rem;
    }

    .progress-fill {
      height: 100%;
      background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan));
      border-radius: 3px;
      transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .chart-section {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 2rem;
      backdrop-filter: blur(12px);
      margin-bottom: 2rem;
      animation: fadeInUp 1s ease-out 0.4s both;
    }

    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.5rem;
    }

    .section-title {
      font-size: 1.5rem;
      font-weight: 700;
      color: var(--text-primary);
    }

    .chart-controls {
      display: flex;
      gap: 0.5rem;
    }

    .control-btn {
      padding: 0.5rem 1rem;
      background: rgba(59, 158, 255, 0.1);
      border: 1px solid var(--border);
      border-radius: 8px;
      color: var(--text-secondary);
      font-size: 0.875rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .control-btn:hover {
      background: rgba(59, 158, 255, 0.2);
      color: var(--accent-blue);
      border-color: var(--accent-blue);
    }

    .chart-wrapper {
      position: relative;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: var(--shadow-sm);
    }

    .chart-wrapper img {
      width: 100%;
      display: block;
      background: #fff;
      transition: transform 0.3s ease;
    }

    .chart-wrapper:hover img {
      transform: scale(1.01);
    }

    .insights-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 1.25rem;
      margin-bottom: 2rem;
      animation: fadeInUp 1.2s ease-out 0.6s both;
    }

    .insight-card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 1.5rem;
      backdrop-filter: blur(12px);
      transition: all 0.3s ease;
    }

    .insight-card:hover {
      background: var(--surface-hover);
      border-color: var(--border-hover);
      box-shadow: var(--shadow-md);
    }

    .insight-header {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      margin-bottom: 1rem;
    }

    .insight-icon {
      width: 40px;
      height: 40px;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.5rem;
      background: linear-gradient(135deg, rgba(59, 158, 255, 0.2), rgba(0, 212, 255, 0.2));
    }

    .insight-title {
      font-size: 1rem;
      font-weight: 600;
      color: var(--text-primary);
    }

    .insight-content {
      color: var(--text-secondary);
      line-height: 1.6;
      font-size: 0.9375rem;
    }

    .tabs {
      display: flex;
      gap: 0.5rem;
      margin-bottom: 1.5rem;
      border-bottom: 1px solid var(--border);
      padding-bottom: 0.5rem;
    }

    .tab {
      padding: 0.75rem 1.5rem;
      background: transparent;
      border: none;
      color: var(--text-secondary);
      font-size: 0.9375rem;
      font-weight: 600;
      cursor: pointer;
      border-radius: 8px 8px 0 0;
      transition: all 0.2s ease;
      position: relative;
    }

    .tab:hover {
      color: var(--text-primary);
      background: rgba(59, 158, 255, 0.05);
    }

    .tab.active {
      color: var(--accent-blue);
      background: rgba(59, 158, 255, 0.1);
    }

    .tab.active::after {
      content: '';
      position: absolute;
      bottom: -0.5rem;
      left: 0;
      right: 0;
      height: 2px;
      background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan));
    }

    .tab-content {
      display: none;
      animation: fadeIn 0.3s ease;
    }

    .tab-content.active {
      display: block;
    }

    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }

    .artifact-links {
      display: flex;
      gap: 1rem;
      flex-wrap: wrap;
    }

    .artifact-link {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.875rem 1.5rem;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 10px;
      color: var(--accent-blue);
      text-decoration: none;
      font-weight: 600;
      transition: all 0.3s ease;
    }

    .artifact-link:hover {
      background: var(--surface-hover);
      border-color: var(--accent-blue);
      transform: translateY(-2px);
      box-shadow: var(--shadow-md);
    }

    .code-block {
      background: var(--bg-secondary);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 1.5rem;
      overflow-x: auto;
      font-family: 'Monaco', 'Menlo', monospace;
      font-size: 0.875rem;
      line-height: 1.6;
      color: var(--text-secondary);
    }

    .skeleton {
      background: linear-gradient(90deg, rgba(60, 80, 110, 0.1) 25%, rgba(60, 80, 110, 0.2) 50%, rgba(60, 80, 110, 0.1) 75%);
      background-size: 200% 100%;
      animation: shimmer 1.5s infinite;
      border-radius: 8px;
    }

    @keyframes shimmer {
      0% { background-position: 200% 0; }
      100% { background-position: -200% 0; }
    }

    @media (max-width: 768px) {
      .container {
        padding: 1.5rem 1rem 3rem;
      }

      .title-section {
        flex-direction: column;
        gap: 1rem;
      }

      .metrics-grid {
        grid-template-columns: 1fr;
      }

      .chart-section {
        padding: 1.5rem;
      }

      .section-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
      }
    }
  </style>
</head>
<body>
  <div class=\"container\">
    <header class=\"header\">
      <div class=\"title-section\">
        <div class=\"title-wrapper\">
          <h1>Quantitative Trading Analytics</h1>
          <p class=\"subtitle\">Statistical Arbitrage Performance Dashboard</p>
        </div>
        <div class=\"status-badge\">
          <span class=\"status-dot\"></span>
          <span id=\"pair-badge\">Loading pair...</span>
        </div>
      </div>
    </header>

    <section class=\"metrics-grid\" id=\"metrics-grid\">
      <div class=\"metric-card skeleton\" style=\"height: 160px;\"></div>
      <div class=\"metric-card skeleton\" style=\"height: 160px;\"></div>
      <div class=\"metric-card skeleton\" style=\"height: 160px;\"></div>
      <div class=\"metric-card skeleton\" style=\"height: 160px;\"></div>
    </section>

    <section class=\"insights-grid\" id=\"insights-grid\"></section>

    <section class=\"chart-section\">
      <div class=\"section-header\">
        <h2 class=\"section-title\">Portfolio Performance</h2>
        <div class=\"chart-controls\">
          <button class=\"control-btn\" onclick=\"window.open('/equity.png', '_blank')\">Expand</button>
        </div>
      </div>
      <div class=\"chart-wrapper\">
        <img src=\"/equity.png\" alt=\"Portfolio Equity Curve\" />
      </div>
    </section>

    <section class=\"chart-section\">
      <div class=\"tabs\">
        <button class=\"tab active\" onclick=\"switchTab('artifacts')\">Artifacts</button>
        <button class=\"tab\" onclick=\"switchTab('summary')\">Raw Data</button>
      </div>

      <div id=\"tab-artifacts\" class=\"tab-content active\">
        <div class=\"artifact-links\">
          <a href=\"/report.md\" target=\"_blank\" class=\"artifact-link\">
            <span>📄</span>
            <span>Performance Report</span>
          </a>
          <a href=\"/summary.json\" target=\"_blank\" class=\"artifact-link\">
            <span>📊</span>
            <span>Summary JSON</span>
          </a>
        </div>
      </div>

      <div id=\"tab-summary\" class=\"tab-content\">
        <div class=\"code-block\">
          <pre id=\"summary-dump\">Loading data...</pre>
        </div>
      </div>
    </section>
  </div>

  <script>
    function switchTab(tabName) {
      document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

      event.target.classList.add('active');
      document.getElementById(`tab-${tabName}`).classList.add('active');
    }

    function animateValue(element, start, end, duration, formatter) {
      const startTime = performance.now();

      function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easeProgress = 1 - Math.pow(1 - progress, 3);
        const current = start + (end - start) * easeProgress;

        element.textContent = formatter(current);

        if (progress < 1) {
          requestAnimationFrame(update);
        }
      }

      requestAnimationFrame(update);
    }

    function formatMetric(key, value) {
      if (typeof value !== 'number') return String(value);
      const lowered = key.toLowerCase();
      if (lowered.includes('drawdown') || lowered.includes('rate') || lowered.includes('cagr')) {
        return `${(value * 100).toFixed(2)}%`;
      }
      return value.toFixed(3);
    }

    function getMetricIcon(key) {
      const lowered = key.toLowerCase();
      if (lowered.includes('sharpe')) return '📈';
      if (lowered.includes('drawdown')) return '📉';
      if (lowered.includes('cagr')) return '💰';
      if (lowered.includes('win')) return '🎯';
      return '📊';
    }

    function getMetricProgress(key, value) {
      const lowered = key.toLowerCase();
      if (lowered.includes('sharpe')) return Math.min((value / 3) * 100, 100);
      if (lowered.includes('drawdown')) return Math.max((1 - value) * 100, 0);
      if (lowered.includes('rate') || lowered.includes('cagr')) return Math.min(value * 100, 100);
      return 0;
    }

    function createInsights(summary) {
      const insights = [];

      if (summary.target_achieved) {
        insights.push({
          icon: '🎉',
          title: 'Target Achieved',
          content: `Strategy successfully exceeded the Sharpe ratio target of ${summary.target_sharpe_ratio}, demonstrating strong risk-adjusted returns.`
        });
      }

      const sharpe = summary.metrics['Sharpe Ratio'];
      if (sharpe > 2.5) {
        insights.push({
          icon: '⭐',
          title: 'Exceptional Performance',
          content: 'The strategy shows outstanding risk-adjusted returns, significantly outperforming typical market benchmarks.'
        });
      } else if (sharpe > 1.5) {
        insights.push({
          icon: '✨',
          title: 'Strong Performance',
          content: 'Risk-adjusted returns indicate a robust trading strategy with consistent alpha generation.'
        });
      }

      const winRate = summary.metrics['Win Rate'];
      if (winRate > 0.6) {
        insights.push({
          icon: '🎯',
          title: 'High Win Rate',
          content: `With a ${(winRate * 100).toFixed(1)}% win rate, the strategy demonstrates reliable trade selection and execution.`
        });
      }

      return insights;
    }

    fetch('/summary.json')
      .then((r) => r.ok ? r.json() : Promise.reject(new Error('summary not found')))
      .then((summary) => {
        document.getElementById('pair-badge').textContent = `${summary.selected_pair.join(' / ')}`;

        const metricsGrid = document.getElementById('metrics-grid');
        metricsGrid.innerHTML = '';

        Object.entries(summary.metrics || {}).forEach(([key, value], index) => {
          const card = document.createElement('article');
          card.className = 'metric-card';
          card.style.animationDelay = `${index * 0.1}s`;

          const progress = getMetricProgress(key, value);
          const isPositive = key.includes('Sharpe') || key.includes('CAGR') || key.includes('Win');

          card.innerHTML = `
            <div class=\"metric-header\">
              <span class=\"metric-label\">${key}</span>
              <div class=\"metric-icon\">${getMetricIcon(key)}</div>
            </div>
            <div class=\"metric-value\" data-value=\"${value}\" data-key=\"${key}\">0</div>
            ${progress > 0 ? `
              <div class=\"progress-bar\">
                <div class=\"progress-fill\" style=\"width: 0%\" data-target=\"${progress}\"></div>
              </div>
            ` : ''}
          `;

          metricsGrid.appendChild(card);

          setTimeout(() => {
            const valueEl = card.querySelector('.metric-value');
            const numValue = typeof value === 'number' ? value : 0;
            animateValue(valueEl, 0, numValue, 1500, (v) => formatMetric(key, v));

            const progressFill = card.querySelector('.progress-fill');
            if (progressFill) {
              setTimeout(() => {
                progressFill.style.width = `${progress}%`;
              }, 200);
            }
          }, index * 100);
        });

        const targetCard = document.createElement('article');
        targetCard.className = 'metric-card';
        targetCard.style.animationDelay = `${Object.keys(summary.metrics).length * 0.1}s`;

        const statusClass = summary.target_achieved ? 'positive' : 'negative';
        const statusText = summary.target_achieved ? 'Target Met' : 'Below Target';
        const statusIcon = summary.target_achieved ? '↗' : '→';

        targetCard.innerHTML = `
          <div class=\"metric-header\">
            <span class=\"metric-label\">Target Objective</span>
            <div class=\"metric-icon\">🎯</div>
          </div>
          <div class=\"metric-value\">${summary.target_sharpe_ratio.toFixed(2)}</div>
          <div class=\"metric-change ${statusClass}\">
            <span>${statusIcon}</span>
            <span>${statusText}</span>
          </div>
        `;

        metricsGrid.appendChild(targetCard);

        const insights = createInsights(summary);
        const insightsGrid = document.getElementById('insights-grid');

        insights.forEach((insight, index) => {
          const card = document.createElement('div');
          card.className = 'insight-card';
          card.style.animationDelay = `${0.8 + index * 0.1}s`;
          card.innerHTML = `
            <div class=\"insight-header\">
              <div class=\"insight-icon\">${insight.icon}</div>
              <h3 class=\"insight-title\">${insight.title}</h3>
            </div>
            <p class=\"insight-content\">${insight.content}</p>
          `;
          insightsGrid.appendChild(card);
        });

        document.getElementById('summary-dump').textContent = JSON.stringify(summary, null, 2);
      })
      .catch((error) => {
        document.getElementById('summary-dump').textContent = `Error loading data: ${error.message}`;
        document.getElementById('pair-badge').textContent = 'Error loading pair';
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
