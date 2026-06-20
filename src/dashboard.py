import json
import os
import glob
from http.server import HTTPServer, SimpleHTTPRequestHandler


def get_latest_alerts(output_dir):
    """Find the most recent alerts file in the output folder."""
    # Get all alert files and sort by name (newest last since they have timestamps)
    files = glob.glob(os.path.join(output_dir, "alerts_*.json"))
    if not files:
        return []
    latest = sorted(files)[-1]
    with open(latest) as f:
        return json.load(f)


def build_html(alerts):
    """Build a cute dashboard HTML page with lilac theme."""

    # Count alerts by severity
    severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for alert in alerts:
        severity_counts[alert["severity"]] += 1

    # Build alert cards HTML
    alert_cards = ""
    for alert in sorted(alerts, key=lambda a: {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}[a["severity"]]):
        # Pick badge color based on severity
        badge_colors = {
            "CRITICAL": "D63384_1",
            "HIGH": "E85D75_1",
            "MEDIUM": "C084FC_1",
            "LOW": "A78BFA_1",
        }
        color = badge_colors[alert["severity"]]

        # Build sample events rows
        event_rows = ""
        for event in alert["sample_events"]:
            event_rows += f"""                <tr>
                    <td>{event['timestamp']}</td>
                    <td>{event['event_name']}</td>
                    <td>{event['user']}</td>
                    <td>{event['source_ip']}</td>
                </tr>
"""

        alert_cards += f"""
        <div class="alert-card">
            <div class="alert-header">
                <span class="badge" style="background:{color}">{alert['severity']}</span>
                <span class="alert-title">{alert['rule']}</span>
            </div>
            <p class="alert-desc">{alert['description']}</p>
            <p class="match-count">Matched <strong>{alert['match_count']}</strong> events</p>
            <table>
                <tr><th>Timestamp</th><th>Event</th><th>User</th><th>Source IP</th></tr>
{event_rows}
            </table>
        </div>
        """

    # Full HTML page with lilac/purple styling
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>SOC-Lite Dashboard</title>
    <meta charset="utf-8">
    <link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Quicksand', sans-serif;
            background: linear-gradient(135deg, #F3E8FF, #EDE4FF, #FAF5FF);
            min-height: 100vh;
            padding: 40px;
        }}
        h1 {{
            text-align: center;
            color: #6B21A8;
            font-size: 2.2em;
            margin-bottom: 10px;
        }}
        .subtitle {{
            text-align: center;
            color: #7C3AED;
            margin-bottom: 30px;
            font-size: 1.1em;
        }}
        .summary {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 40px;
            flex-wrap: wrap;
        }}
        .summary-card {{
            background: white;
            border-radius: 16px;
            padding: 20px 30px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(139, 92, 246, 0.15);
            min-width: 140px;
        }}
        .summary-card .count {{
            font-size: 2em;
            font-weight: bold;
            color: #6B21A8;
        }}
        .summary-card .label {{
            color: #8B5CF6;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        .alert-card {{
            background: white;
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(139, 92, 246, 0.1);
            border-left: 5px solid #C084FC;
        }}
        .alert-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 10px;
        }}
        .badge {{
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
        }}
        .alert-title {{
            font-size: 1.2em;
            color: #4C1D95;
            font-weight: 600;
        }}
        .alert-desc {{
            color: #6B7280;
            margin-bottom: 8px;
        }}
        .match-count {{
            color: #7C3AED;
            margin-bottom: 12px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85em;
        }}
        th {{
            background: #F5F3FF;
            color: #6B21A8;
            padding: 8px 12px;
            text-align: left;
        }}
        td {{
            padding: 8px 12px;
            border-top: 1px solid #EDE9FE;
            color: #4B5563;
        }}
        tr:hover td {{
            background: #FAF5FF;
        }}
    </style>
</head>
<body>
    <h1>&#128737; SOC-Lite Dashboard &#128737;</h1>
    <p class="subtitle">Security Alert Report</p>

    <div class="summary">
        <div class="summary-card">
            <div class="count">{len(alerts)}</div>
            <div class="label">Total Rules Triggered</div>
        </div>
        <div class="summary-card">
            <div class="count">{severity_counts['HIGH'] + severity_counts['CRITICAL']}</div>
            <div class="label">High/Critical</div>
        </div>
        <div class="summary-card">
            <div class="count">{severity_counts['MEDIUM']}</div>
            <div class="label">Medium</div>
        </div>
        <div class="summary-card">
            <div class="count">{severity_counts['LOW']}</div>
            <div class="label">Low</div>
        </div>
    </div>

{alert_cards}
    <script>
        window.onload = function() {{
            const jokes = [
                "🚨 ALERT: Unauthorized vibes detected in your network. Initiating cuteness protocol... 💜",
                "⚠️ Heads up: suspicious giggles detected. Deploying plushy countermeasures... 🧸",
                "🔔 Warning: Someone\'s being sneaky. Launching dance-off deterrent... 💃",
                "🛡️ Alert: Unexpected vibes incoming. Activating cookie brigade... 🍪",
                "🐱‍👤 Notice: Stealthy shenanigans detected. Summoning ninja kittens... 😼",
            ];
            const msg = jokes[Math.floor(Math.random() * jokes.length)];
            setTimeout(function() {{
                alert(msg);
            }}, 500);
        }};
    </script>
</body>
</html>"""

    return html


def run_dashboard(port=8080):
    """Start a local web server that shows the dashboard."""

    # Get alerts from the most recent output file
    root = os.path.join(os.path.dirname(__file__), "..")
    output_dir = os.path.join(root, "output")
    alerts = get_latest_alerts(output_dir)

    # Build the HTML page
    html = build_html(alerts)

    # Save it to a file the web server can serve
    dashboard_path = os.path.join(root, "output", "dashboard.html")
    with open(dashboard_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[+] Dashboard ready! Open your browser to: http://localhost:{port}/dashboard.html")

    # Start a simple web server from the output folder
    os.chdir(os.path.join(root, "output"))
    server = HTTPServer(("localhost", port), SimpleHTTPRequestHandler)
    server.serve_forever()


if __name__ == "__main__":
    run_dashboard()