"""
Pinterest Analytics Web Dashboard
Local web server with beautiful charts and tables
"""

import json
import os
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import webbrowser

# Dashboard port
PORT = 8080


def get_dashboard_html(data: dict) -> str:
    """Generate dashboard HTML with ECharts"""
    
    account = data.get('account', {})
    boards = data.get('boards', [])
    metrics = data.get('metrics', {})
    comparison = data.get('comparison', {})
    alerts = data.get('alerts', [])
    
    # Prepare chart data
    board_names = [b.get('name', 'Unknown')[:20] for b in boards[:10]]
    board_pins = [b.get('pin_count', 0) or 0 for b in boards[:10]]
    board_followers = [b.get('follower_count', 0) or 0 for b in boards[:10]]
    
    html = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pinterest Analytics Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            min-height: 100vh;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            padding: 30px 0;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            background: linear-gradient(90deg, #E60023, #ff6b6b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            color: #888;
            font-size: 1.1rem;
        }}
        
        .dashboard {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 24px;
            border: 1px solid rgba(255,255,255,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 40px rgba(230,0,35,0.2);
        }}
        
        .stat-card .label {{
            color: #888;
            font-size: 0.9rem;
            margin-bottom: 8px;
        }}
        
        .stat-card .value {{
            font-size: 2rem;
            font-weight: bold;
            color: #fff;
        }}
        
        .stat-card .change {{
            font-size: 0.85rem;
            margin-top: 8px;
        }}
        
        .stat-card .change.positive {{
            color: #4ade80;
        }}
        
        .stat-card .change.negative {{
            color: #f87171;
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .chart-card {{
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 24px;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        
        .chart-card h3 {{
            margin-bottom: 20px;
            color: #fff;
        }}
        
        .chart {{
            width: 100%;
            height: 300px;
        }}
        
        .alerts {{
            margin-bottom: 30px;
        }}
        
        .alert {{
            padding: 16px 20px;
            border-radius: 12px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        
        .alert.warning {{
            background: rgba(251, 191, 36, 0.1);
            border: 1px solid rgba(251, 191, 36, 0.3);
            color: #fbbf24;
        }}
        
        .alert.success {{
            background: rgba(74, 222, 128, 0.1);
            border: 1px solid rgba(74, 222, 128, 0.3);
            color: #4ade80;
        }}
        
        .alert.info {{
            background: rgba(96, 165, 250, 0.1);
            border: 1px solid rgba(96, 165, 250, 0.3);
            color: #60a5fa;
        }}
        
        .table-card {{
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 24px;
            border: 1px solid rgba(255,255,255,0.1);
            overflow-x: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th, td {{
            padding: 12px 16px;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        
        th {{
            color: #888;
            font-weight: 500;
            font-size: 0.85rem;
            text-transform: uppercase;
        }}
        
        tr:hover {{
            background: rgba(255,255,255,0.05);
        }}
        
        .footer {{
            text-align: center;
            padding: 40px 0;
            color: #666;
        }}
        
        .refresh-btn {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: #E60023;
            color: #fff;
            border: none;
            padding: 16px 24px;
            border-radius: 50px;
            font-size: 1rem;
            cursor: pointer;
            box-shadow: 0 4px 20px rgba(230,0,35,0.4);
            transition: transform 0.2s;
        }}
        
        .refresh-btn:hover {{
            transform: scale(1.05);
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        <header class="header">
            <h1>Pinterest Analytics</h1>
            <p class="subtitle">@{account.get('username', 'Unknown')} • {datetime.now().strftime('%d %B %Y, %H:%M')}</p>
        </header>
        
        <!-- Alerts -->
        <div class="alerts">
            {''.join([f'<div class="alert {a.get("type", "info").lower()}">{"⚠️" if a.get("type") == "WARNING" else "✅" if a.get("type") == "SUCCESS" else "ℹ️"} {a.get("message", "")}</div>' for a in alerts])}
        </div>
        
        <!-- Stats Cards -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="label">Total Pins</div>
                <div class="value">{metrics.get('total_pins', 0):,}</div>
            </div>
            <div class="stat-card">
                <div class="label">Boards</div>
                <div class="value">{metrics.get('boards_count', 0):,}</div>
            </div>
            <div class="stat-card">
                <div class="label">Followers</div>
                <div class="value">{account.get('follower_count', 0) or 0:,}</div>
            </div>
            <div class="stat-card">
                <div class="label">Following</div>
                <div class="value">{account.get('following_count', 0) or 0:,}</div>
            </div>
            <div class="stat-card">
                <div class="label">Monthly Views</div>
                <div class="value">{account.get('monthly_views', 0) or 0:,}</div>
            </div>
        </div>
        
        <!-- Charts -->
        <div class="charts-grid">
            <div class="chart-card">
                <h3>Top Boards by Pins</h3>
                <div id="boardsPinsChart" class="chart"></div>
            </div>
            <div class="chart-card">
                <h3>Top Boards by Followers</h3>
                <div id="boardsFollowersChart" class="chart"></div>
            </div>
        </div>
        
        <!-- Boards Table -->
        <div class="table-card">
            <h3 style="margin-bottom: 20px;">All Boards</h3>
            <table>
                <thead>
                    <tr>
                        <th>Board Name</th>
                        <th>Pins</th>
                        <th>Followers</th>
                        <th>Privacy</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f"<tr><td>{b.get('name', 'Unknown')}</td><td>{b.get('pin_count', 0) or 0:,}</td><td>{b.get('follower_count', 0) or 0:,}</td><td>{b.get('privacy', 'PUBLIC')}</td></tr>" for b in boards])}
                </tbody>
            </table>
        </div>
        
        <footer class="footer">
            <p>Pinterest Analytics Dashboard • Built with python-pinterest SDK</p>
        </footer>
    </div>
    
    <button class="refresh-btn" onclick="location.reload()">🔄 Refresh</button>
    
    <script>
        // Board Pins Chart
        var boardsPinsChart = echarts.init(document.getElementById('boardsPinsChart'));
        boardsPinsChart.setOption({{
            tooltip: {{ trigger: 'axis' }},
            xAxis: {{
                type: 'category',
                data: {json.dumps(board_names)},
                axisLabel: {{ color: '#888', rotate: 45 }}
            }},
            yAxis: {{
                type: 'value',
                axisLabel: {{ color: '#888' }},
                splitLine: {{ lineStyle: {{ color: 'rgba(255,255,255,0.1)' }} }}
            }},
            series: [{{
                data: {json.dumps(board_pins)},
                type: 'bar',
                itemStyle: {{
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        {{ offset: 0, color: '#E60023' }},
                        {{ offset: 1, color: '#ff6b6b' }}
                    ])
                }},
                barRadius: [8, 8, 0, 0]
            }}]
        }});
        
        // Board Followers Chart
        var boardsFollowersChart = echarts.init(document.getElementById('boardsFollowersChart'));
        boardsFollowersChart.setOption({{
            tooltip: {{ trigger: 'item' }},
            series: [{{
                type: 'pie',
                radius: ['40%', '70%'],
                avoidLabelOverlap: false,
                itemStyle: {{
                    borderRadius: 10,
                    borderColor: '#1a1a2e',
                    borderWidth: 2
                }},
                label: {{
                    show: true,
                    color: '#fff'
                }},
                data: {json.dumps([{'name': n, 'value': v} for n, v in zip(board_names, board_followers) if v > 0])}
            }}]
        }});
        
        // Resize charts on window resize
        window.addEventListener('resize', function() {{
            boardsPinsChart.resize();
            boardsFollowersChart.resize();
        }});
    </script>
</body>
</html>'''
    
    return html


class DashboardHandler(SimpleHTTPRequestHandler):
    """Custom handler for dashboard"""
    
    dashboard_data = {}
    
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = get_dashboard_html(self.dashboard_data)
            self.wfile.write(html.encode('utf-8'))
        elif self.path == '/api/data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(self.dashboard_data, default=str).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Suppress logging


def start_dashboard(analytics, port: int = PORT):
    """Start the dashboard server"""
    print(f"Fetching data...")
    
    # Get data
    try:
        summary = analytics.get_summary()
        boards = analytics.get_boards()
        
        data = {
            'account': summary.get('account', {}),
            'boards': boards,
            'metrics': {
                'total_pins': summary.get('total_pins', 0),
                'boards_count': summary.get('boards_count', 0),
                'total_followers': summary.get('total_followers', 0),
            },
            'comparison': {},
            'alerts': [],
        }
        
        DashboardHandler.dashboard_data = data
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        DashboardHandler.dashboard_data = {
            'account': {'username': 'Error'},
            'boards': [],
            'metrics': {},
            'alerts': [{'type': 'WARNING', 'message': str(e)}],
        }
    
    # Start server
    server = HTTPServer(('localhost', port), DashboardHandler)
    
    print(f"\n{'='*50}")
    print(f"Dashboard running at: http://localhost:{port}")
    print(f"{'='*50}")
    print("Press Ctrl+C to stop\n")
    
    # Open browser
    webbrowser.open(f'http://localhost:{port}')
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping dashboard...")
        server.shutdown()


if __name__ == '__main__':
    from analytics import get_analytics
    analytics = get_analytics()
    start_dashboard(analytics)
