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
            "CRITICAL": "#dc2626",
            "HIGH": "#ea580c",
            "MEDIUM": "#eab308",
            "LOW": "#22c55a",
        }
        color = badge_colors[alert["severity"]]

        # Build sample events rows
        event_rows = ""
        for event in alert["sample_events"]:
            event_rows += f"""                <tr onclick="window.location='logs.html#event-{event['timestamp']}'" style="cursor:pointer" title="Click to view all logs">
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
    <link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600;700&family=Orbitron:wght@500;700&family=Audiowide&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
        font-family: 'Quicksand', sans-serif;
        background: linear-gradient(135deg, #0F0C29, #302B63, #24243E);
        min-height: 100vh;
        padding: 40px;
        color: #E2E8F0;
    }}
    h1 {{
        text-align: center;
        margin-bottom: 10px;
        perspective: 900px;
    }}

    .title-text {{
        display: inline-block;
        font-family: 'Audiowide', 'Orbitron', 'Quicksand', sans-serif;
        font-weight: 700;
        font-size: 2.6em;
        line-height: 1;
        position: relative;
        letter-spacing: 1px;
        /* cyber palette gradient */
        background: linear-gradient(90deg, #06b6d4, #7c3aed, #06b6d4);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shimmer 3s linear infinite;
        transform-style: preserve-3d;
        will-change: transform;
        /* subtle cyan glow and light outline for readability (no heavy black shadow) */
        text-shadow: 0 8px 30px rgba(6,182,212,0.10), 0 1px 0 rgba(0,0,0,0.08);
            text-transform: uppercase; /* Added uppercase transformation */
    }}

    /* Deep, layered extrusion to make the title feel like it's coming off the screen */
    .title-text::before {{
        content: attr(data-text);
        position: absolute;
        left: 0;
        top: 0;
        z-index: -3;
        color: rgba(2,6,23,0.98);
        transform: translateY(20px) skewX(-8deg) scaleY(0.99);
        filter: blur(0px);
        opacity: 1;
    }}

    /* Colored glow layer between the main text and the deep shadow */
    .title-text::after {{
        content: attr(data-text);
        position: absolute;
        left: 0;
        top: 0;
        z-index: -2;
        color: #06b6d4;
        transform: translateY(6px);
        filter: blur(6px);
        opacity: 0.75;
        mix-blend-mode: screen;
    }}
    @keyframes shimmer {{
        0% {{ background-position: 0% center; }}
        100% {{ background-position: 200% center; }}
    }}
    .shield {{
        display: inline-block;
        font-size: 2.5em;
        animation: spin3d 3s ease-in-out infinite;
        filter: drop-shadow(0 0 10px rgba(167, 139, 250, 0.6));
    }}

    /* Make emoji shields visible even though h1 uses a transparent text-fill
       for the gradient title. Force a solid color and ensure the emoji
       doesn't inherit the gradient clipping. */
    .shield {{
        -webkit-text-fill-color: initial;
        -webkit-text-fill-color: currentColor;
        color: #FDE68A; /* soft gold so the shields pop */
        /* reduced black shadow plus a light gold glow */
        text-shadow: 0 1px 3px rgba(0,0,0,0.18), 0 0 8px rgba(253,230,138,0.06);
        will-change: transform;
    }}
    @keyframes spin3d {{
        0% {{ transform: rotateY(0deg); }}
        50% {{ transform: rotateY(180deg); }}
        100% {{ transform: rotateY(360deg); }}
    }}
    .subtitle {{
        text-align: center;
        color: #A78BFA;
        margin-bottom: 30px;
        font-size: 1.1em;
        letter-spacing: 2px;
        text-transform: uppercase;
    }}
    .summary {{
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-bottom: 40px;
        flex-wrap: wrap;
    }}
    .summary-card {{
        /* Slightly lighter than background and a soft black shadow to lift the "tab" */
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(167, 139, 250, 0.22);
        border-radius: 20px;
        padding: 24px 32px;
        text-align: center;
        min-width: 150px;
        transition: transform 0.25s, box-shadow 0.25s, background 0.25s;
        box-shadow: 0 8px 20px rgba(0,0,0,0.28);
    }}
    .summary-card:hover {{
        transform: translateY(-6px);
        box-shadow: 0 14px 44px rgba(0,0,0,0.36), 0 3px 8px rgba(167,139,250,0.12);
    }}
    .summary-card .count {{
        font-size: 2.4em;
        font-weight: bold;
        background: linear-gradient(135deg, #C084FC, #F472B6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    .summary-card .label {{
        color: #94A3B8;
        font-size: 0.9em;
        margin-top: 5px;
    }}
    .alert-card {{
        /* Make the alert card feel like a raised tab with a darker shadow */
        background: rgba(255, 255, 255, 0.045);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(167, 139, 250, 0.14);
        border-radius: 18px;
        padding: 26px;
        margin-bottom: 20px;
        transition: transform 0.25s, box-shadow 0.25s;
        animation: floatIn 0.45s ease-out;
        box-shadow: 0 10px 30px rgba(0,0,0,0.32);
    }}

    .alert-card:hover {{
        transform: translateY(-6px) scale(1.01);
        box-shadow: 0 20px 60px rgba(0,0,0,0.38), 0 6px 18px rgba(167,139,250,0.08);
        border-color: rgba(167, 139, 250, 0.42);
    }}

    @keyframes floatIn {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    .alert-header {{
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 14px;
    }}
    .alert-title {{
        font-size: 1.2em;
        color: #E2E8F0;
        font-weight: 800;
        letter-spacing: 0.2px;
        display: block;
        margin-top: 2px;
    }}
    .badge {{
        color: white;
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 0.75em;
        font-weight: bold;
        letter-spacing: 1px;
    }}
    .alert-desc {{
        color: #94A3B8;
        margin-bottom: 10px;
        font-size: 0.95em;
    }}
    .match-count {{
        color: #C084FC;
        margin-bottom: 14px;
        font-weight: 600;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 0.85em;
        border-radius: 12px;
        overflow: hidden;
    }}
    th {{
        background: rgba(167, 139, 250, 0.15);
        color: #C084FC;
        padding: 10px 14px;
        text-align: left;
        font-weight: 600;
        letter-spacing: 0.5px;
    }}
    td {{
        padding: 10px 14px;
        /* unified subtle separator instead of purple lines */
        border-bottom: 1px solid rgba(255,255,255,0.03);
        color: #CBD5E1;
    }}
    tr:hover td {{
        background: rgba(167, 139, 250, 0.08);
    }}
    tr {{
        cursor: pointer;
    }}
    .footer {{
        text-align: center;
        margin-top: 40px;
        color: #64748B;
        font-size: 0.85em;
    }}
    .footer a {{
        color: #A78BFA;
        text-decoration: none;
    }}
</style>
</head>
<body>
    <h1><span class="shield">&#128737;</span> <span class="title-text" data-text="SOC-Lite Dashboard">SOC-Lite Dashboard</span> <span class="shield">&#128737;</span></h1>
    <p class="subtitle">Security Alert Report</p>

    <div class="summary">
        <div class="summary-card">
            <div class="count">{len(alerts)}</div>
            <div class="label">Total Rules Triggered</div>
    </div>
    <div class="summary-card">
        <div class="count">{severity_counts['HIGH'] + severity_counts['CRITICAL']}</div>
        <div class="label">High / Critical</div>
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

    <div class="footer">
        Built by Leilany Rojas | Data from <a href="https://github.com/OTRF/Security-Datasets">OTRF Security Datasets</a> | Rules mapped to <a href="https://attack.mitre.org/">MITRE ATT&CK</a>
    </div>
</body>
</html>"""
    return html

def build_logs_html(db_path):
    """Build a page showing all logs so users can see full event details."""
    import sqlite3
    conn = sqlite3.connect(db_path)
    # Get every event from the database
    rows = conn.execute("SELECT rowid, timestamp, event_name, user, source_ip, event_source, principle_type, raw_log FROM events ORDER BY timestamp").fetchall()
    conn.close()

    # Build a table row for each event, with an anchor ID for linking
    table_rows = ""
    for row in rows:
        table_rows += f"""
        <tr id="event-{row[1]}">
            <td>{row[0]}</td>
            <td>{row[1]}</td>
            <td>{row[2]}</td>
            <td>{row[3]}</td>
            <td>{row[4]}</td>
            <td>{row[5]}</td>
            <td>{row[6]}</td>
            <td><details><summary>View</summary></details></td>
        </tr>
        <tr class="raw-log-row" style="display:none">
            <td colspan="8"><pre style="white-space:pre-wrap;word-break:break-all;font-size:0.75em;background:#000000;padding:12px;border-radius:8px;max-width:100%">{json.dumps(json.loads(row[7]), indent=2) if row[7] else"N/A"}</pre></td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>SOC-Lite - All Logs</title>
    <meta charset="utf-8">
    <link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600;700&family=Orbitron:wght@500;700&family=Audiowide&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Quicksand', sans-serif;
            background: linear-gradient(135deg, #0F0C29, #302B63, #24243E);
            min-height: 100vh;
            padding: 40px;
            color: #E2E8F0;
        }}
        h1 {{
            text-align: center;
            font-family: 'Audiowide', 'Orbitron', 'Quicksand', sans-serif;
            color: #E2E8F0;
            font-size: 1.8em;
            margin-bottom: 18px;
            letter-spacing: 1px;
            text-shadow: 0 2px 8px rgba(0,0,0,0.6);
        }}
        .back-btn {{
            display: inline-block;
            margin: 0 0 24px 0;
            background: rgba(255,255,255,0.06);
            color: #E2E8F0;
            padding: 8px 18px;
            border-radius: 16px;
            text-decoration: none;
            font-weight: 600;
            border: 1px solid rgba(167,139,250,0.12);
            box-shadow: 0 6px 20px rgba(0,0,0,0.36);
        }}
        .back-btn:hover {{
            transform: translateY(-3px);
            box-shadow: 0 12px 36px rgba(0,0,0,0.42);
        }}
        .logs-card {{
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(167,139,250,0.12);
            border-radius: 14px;
            padding: 18px;
            box-shadow: 0 8px 26px rgba(0,0,0,0.32);
            overflow: auto;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9em;
            color: #E2E8F0;
        }}
        th {{
            background: rgba(167,139,250,0.12);
            color: #C084FC;
            padding: 10px 12px;
            text-align: left;
            font-weight: 700;
        }}
        td {{
            padding: 10px 12px;
            border-top: 1px solid rgba(167,139,250,0.06);
            vertical-align: top;
            color: #CBD5E1;
        }}
        tr:hover td {{
            background: rgba(167,139,250,0.03);
        }}
        tr:target td {{
            /* Subtle cyber highlight: uniform darker row without bright accent */
            background: rgba(31,41,55,0.48);
            font-weight: 700;
            color: #E6FBFF;
            border-left: none;
            transition: background 200ms ease;
        }}
        .raw-log-row pre {{
            background: rgba(7,10,23,0.85);
            color: #d1fae5;
            padding: 14px;
            border-radius: 8px;
            font-size: 0.78em;
            overflow: auto;
            white-space: pre-wrap;
        }}
        details summary {{
            cursor: pointer;
            color: #A7F3D0;
            font-weight: 600;
        }}
        .controls {{
            margin-bottom: 16px;
        }}
        #searchInput {{
            width: 100%;
            padding: 10px 14px;
            border-radius: 12px;
            border: 1px solid rgba(167,139,250,0.18);
            background: rgba(255,255,255,0.04);
            color: #E2E8F0;
            font-size: 0.95em;
        }}
        #searchInput::placeholder {{
            color: #94A3B8;
        }}
    </style>
</head>
<body>
    <h1>&#128203; All Events Log</h1>
    <a href="index.html" class="back-btn">&#x2190; Back to Dashboard</a>
    <div class="logs-card">
        <div class="controls">
            <input id="searchInput" placeholder="Search logs..." />
        </div>
    <table id="logsTable">
        <tr>
            <th>#</th>
            <th>Timestamp</th>
            <th>Event</th>
            <th>User</th>
            <th>Source IP</th>
            <th>Service</th>
            <th>Principal Type</th>
            <th>Raw Log</th>
        </tr>
        {table_rows}
    </table>
    </div>
<script>
    document.querySelectorAll('details').forEach(function(detail) {{
        detail.addEventListener('toggle', function() {{
            var rawRow = this.closest('tr').nextElementSibling;
            if (this.open) {{
                rawRow.style.display = 'table-row';
            }} else {{
                rawRow.style.display = 'none';
            }}
        }});
    }});

    function filterLogs() {{
        var query = document.getElementById('searchInput').value.toLowerCase();
        document.querySelectorAll('#logsTable tr:not(.raw-log-row)').forEach(function(row) {{
            if (!row.querySelector('td')) return;
            var rowText = row.textContent.toLowerCase();
            var rawRow = row.nextElementSibling;
            var rawText = rawRow ? rawRow.textContent.toLowerCase() : '';
            var visible = query === '' || rowText.indexOf(query) !== -1 || rawText.indexOf(query) !== -1;
            row.style.display = visible ? 'table-row' : 'none';
            if (rawRow) rawRow.style.display = visible && rawRow.style.display === 'table-row' ? 'table-row' : 'none';
        }});
    }}

    document.getElementById('searchInput').addEventListener('input', filterLogs);
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
    dashboard_path = os.path.join(root, "output", "index.html")
    with open(dashboard_path, "w", encoding="utf-8") as f:
        f.write(html)

    # Build the logs page and save it
    logs_html = build_logs_html("soc_lite.db")
    logs_path = os.path.join(root, "output", "logs.html")
    with open(logs_path, "w") as f:
        f.write(logs_html)

    print(f"[+] Dashboard ready! Open your browser to: http://localhost:{port}/index.html")

    # Start a simple web server from the output folder
    os.chdir(os.path.join(root, "output"))
    server = HTTPServer(("localhost", port), SimpleHTTPRequestHandler)
    server.serve_forever()


if __name__ == "__main__":
    run_dashboard()