"""
Pinterest Analytics Web Dashboard v2
Enhanced multi-page dashboard with navigation, charts, and analytics
"""

import json
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser
from urllib.parse import urlparse, parse_qs

PORT = 8080


def get_base_styles() -> str:
    """Get shared CSS styles"""
    return '''
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        :root {
            --pin-red: #E60023;
            --pin-red-dark: #ad081b;
            --bg-dark: #1a1a2e;
            --bg-darker: #16213e;
            --card-bg: rgba(255,255,255,0.05);
            --border: rgba(255,255,255,0.1);
            --text: #fff;
            --text-muted: #888;
            --success: #4ade80;
            --warning: #fbbf24;
            --danger: #f87171;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, var(--bg-dark) 0%, var(--bg-darker) 100%);
            color: var(--text);
            min-height: 100vh;
        }
        
        /* Navigation */
        .nav {
            background: rgba(0,0,0,0.3);
            padding: 0 20px;
            display: flex;
            align-items: center;
            gap: 30px;
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(10px);
        }
        
        .nav-brand {
            font-size: 1.3rem;
            font-weight: bold;
            color: var(--pin-red);
            padding: 15px 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .nav-links {
            display: flex;
            gap: 5px;
        }
        
        .nav-link {
            color: var(--text-muted);
            text-decoration: none;
            padding: 15px 20px;
            border-bottom: 3px solid transparent;
            transition: all 0.2s;
        }
        
        .nav-link:hover, .nav-link.active {
            color: var(--text);
            border-bottom-color: var(--pin-red);
        }
        
        .nav-user {
            margin-left: auto;
            color: var(--text-muted);
            font-size: 0.9rem;
        }
        
        /* Main content */
        .main {
            max-width: 1400px;
            margin: 0 auto;
            padding: 30px 20px;
        }
        
        .page-title {
            font-size: 1.8rem;
            margin-bottom: 30px;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .page-title small {
            font-size: 0.9rem;
            color: var(--text-muted);
            font-weight: normal;
        }
        
        /* Cards */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: var(--card-bg);
            border-radius: 16px;
            padding: 24px;
            border: 1px solid var(--border);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 40px rgba(230,0,35,0.2);
        }
        
        .stat-card .icon {
            font-size: 2rem;
            margin-bottom: 10px;
        }
        
        .stat-card .label {
            color: var(--text-muted);
            font-size: 0.85rem;
            margin-bottom: 5px;
        }
        
        .stat-card .value {
            font-size: 1.8rem;
            font-weight: bold;
        }
        
        .stat-card .change {
            font-size: 0.8rem;
            margin-top: 8px;
        }
        
        .stat-card .change.up { color: var(--success); }
        .stat-card .change.down { color: var(--danger); }
        
        /* Charts grid */
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .chart-card {
            background: var(--card-bg);
            border-radius: 16px;
            padding: 24px;
            border: 1px solid var(--border);
        }
        
        .chart-card h3 {
            margin-bottom: 20px;
            font-size: 1.1rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .chart { width: 100%; height: 300px; }
        .chart-lg { height: 400px; }
        
        /* Tables */
        .table-card {
            background: var(--card-bg);
            border-radius: 16px;
            padding: 24px;
            border: 1px solid var(--border);
            overflow-x: auto;
            margin-bottom: 30px;
        }
        
        .table-card h3 {
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th, td {
            padding: 12px 16px;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }
        
        th {
            color: var(--text-muted);
            font-weight: 500;
            font-size: 0.8rem;
            text-transform: uppercase;
        }
        
        tr:hover { background: rgba(255,255,255,0.03); }
        
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 500;
        }
        
        .badge-success { background: rgba(74,222,128,0.2); color: var(--success); }
        .badge-warning { background: rgba(251,191,36,0.2); color: var(--warning); }
        .badge-danger { background: rgba(248,113,113,0.2); color: var(--danger); }
        
        /* Progress bar */
        .progress {
            height: 8px;
            background: var(--border);
            border-radius: 4px;
            overflow: hidden;
        }
        
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, var(--pin-red), #ff6b6b);
            border-radius: 4px;
            transition: width 0.5s ease;
        }
        
        /* Alerts */
        .alert {
            padding: 16px 20px;
            border-radius: 12px;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .alert-warning {
            background: rgba(251, 191, 36, 0.1);
            border: 1px solid rgba(251, 191, 36, 0.3);
            color: var(--warning);
        }
        
        .alert-success {
            background: rgba(74, 222, 128, 0.1);
            border: 1px solid rgba(74, 222, 128, 0.3);
            color: var(--success);
        }
        
        .alert-info {
            background: rgba(96, 165, 250, 0.1);
            border: 1px solid rgba(96, 165, 250, 0.3);
            color: #60a5fa;
        }
        
        /* Keywords */
        .keyword-cloud {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            padding: 20px 0;
        }
        
        .keyword-tag {
            background: var(--card-bg);
            border: 1px solid var(--border);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
            transition: all 0.2s;
        }
        
        .keyword-tag:hover {
            background: var(--pin-red);
            border-color: var(--pin-red);
        }
        
        .keyword-tag .count {
            color: var(--text-muted);
            font-size: 0.8rem;
            margin-left: 5px;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 40px 20px;
            color: var(--text-muted);
            font-size: 0.9rem;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .charts-grid { grid-template-columns: 1fr; }
            .nav-links { display: none; }
        }
    '''


def get_nav_html(active_page: str, username: str) -> str:
    """Generate navigation HTML"""
    pages = [
        ('/', 'Overview', '📊'),
        ('/boards', 'Boards', '📋'),
        ('/cleanup', 'Cleanup', '🗑️'),
        ('/keywords', 'Keywords', '🔑'),
        ('/trends', 'Trends', '📈'),
    ]
    
    links = ''.join([
        f'<a href="{url}" class="nav-link {"active" if url == active_page else ""}">{icon} {name}</a>'
        for url, name, icon in pages
    ])
    
    return f'''
    <nav class="nav">
        <div class="nav-brand">📌 Pinterest Analytics</div>
        <div class="nav-links">{links}</div>
        <div class="nav-user">@{username} • {datetime.now().strftime('%H:%M')}</div>
    </nav>
    '''


def get_overview_page(data: dict) -> str:
    """Generate overview page HTML"""
    account = data.get('account', {})
    boards = data.get('boards', [])
    metrics = data.get('metrics', {})
    keywords = data.get('keywords', {})
    
    # Prepare chart data
    board_names = [b.get('name', 'Unknown')[:15] for b in boards[:10]]
    board_pins = [b.get('pin_count', 0) or 0 for b in boards[:10]]
    board_followers = [b.get('follower_count', 0) or 0 for b in boards[:10]]
    
    # Calculate efficiency (followers per pin)
    efficiency_data = []
    for b in boards[:10]:
        pins = b.get('pin_count', 0) or 0
        followers = b.get('follower_count', 0) or 0
        if pins > 0:
            efficiency_data.append({
                'name': b.get('name', '')[:15],
                'value': round(followers / pins, 2)
            })
    efficiency_data.sort(key=lambda x: x['value'], reverse=True)
    
    top_keywords = keywords.get('top_keywords', [])[:10]
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pinterest Analytics - Overview</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>{get_base_styles()}</style>
</head>
<body>
    {get_nav_html('/', account.get('username', 'User'))}
    
    <main class="main">
        <h1 class="page-title">📊 Overview <small>Your Pinterest at a glance</small></h1>
        
        <!-- Stats Cards -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="icon">📌</div>
                <div class="label">Total Pins</div>
                <div class="value">{metrics.get('total_pins', 0):,}</div>
            </div>
            <div class="stat-card">
                <div class="icon">📋</div>
                <div class="label">Boards</div>
                <div class="value">{metrics.get('boards_count', 0):,}</div>
            </div>
            <div class="stat-card">
                <div class="icon">👥</div>
                <div class="label">Followers</div>
                <div class="value">{account.get('follower_count', 0) or 0:,}</div>
            </div>
            <div class="stat-card">
                <div class="icon">👀</div>
                <div class="label">Monthly Views</div>
                <div class="value">{account.get('monthly_views', 0) or 0:,}</div>
            </div>
            <div class="stat-card">
                <div class="icon">➡️</div>
                <div class="label">Following</div>
                <div class="value">{account.get('following_count', 0) or 0:,}</div>
            </div>
        </div>
        
        <!-- Charts Row 1 -->
        <div class="charts-grid">
            <div class="chart-card">
                <h3>📊 Pins by Board</h3>
                <div id="pinsChart" class="chart"></div>
            </div>
            <div class="chart-card">
                <h3>👥 Followers by Board</h3>
                <div id="followersChart" class="chart"></div>
            </div>
        </div>
        
        <!-- Charts Row 2 -->
        <div class="charts-grid">
            <div class="chart-card">
                <h3>⚡ Board Efficiency <small style="color:#888;font-weight:normal">(followers per pin)</small></h3>
                <div id="efficiencyChart" class="chart"></div>
            </div>
            <div class="chart-card">
                <h3>🔑 Top Keywords</h3>
                <div class="keyword-cloud">
                    {''.join([f'<span class="keyword-tag">{kw.get("keyword", "")}<span class="count">({kw.get("count", 0)})</span></span>' for kw in top_keywords]) or '<span style="color:#888">Analyze keywords with: python main.py keywords</span>'}
                </div>
            </div>
        </div>
        
        <!-- Top Boards Table -->
        <div class="table-card">
            <h3>📋 Top Boards by Pins</h3>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Board</th>
                        <th>Pins</th>
                        <th>Followers</th>
                        <th>Efficiency</th>
                        <th>Privacy</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f"""<tr>
                        <td>{i+1}</td>
                        <td><strong>{b.get('name', 'Unknown')}</strong></td>
                        <td>{b.get('pin_count', 0) or 0:,}</td>
                        <td>{b.get('follower_count', 0) or 0:,}</td>
                        <td>{round((b.get('follower_count', 0) or 0) / max(b.get('pin_count', 0) or 1, 1), 2)}</td>
                        <td><span class="badge badge-{'success' if b.get('privacy') == 'PUBLIC' else 'warning'}">{b.get('privacy', 'PUBLIC')}</span></td>
                    </tr>""" for i, b in enumerate(sorted(boards, key=lambda x: x.get('pin_count', 0) or 0, reverse=True)[:10])])}
                </tbody>
            </table>
        </div>
    </main>
    
    <footer class="footer">
        Pinterest Analytics Dashboard v2.0 • Built with python-pinterest SDK
    </footer>
    
    <script>
        // Pins Chart
        var pinsChart = echarts.init(document.getElementById('pinsChart'));
        pinsChart.setOption({{
            tooltip: {{ trigger: 'axis' }},
            xAxis: {{
                type: 'category',
                data: {json.dumps(board_names)},
                axisLabel: {{ color: '#888', rotate: 45, fontSize: 11 }}
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
                    ]),
                    borderRadius: [6, 6, 0, 0]
                }}
            }}],
            grid: {{ left: 50, right: 20, bottom: 80, top: 20 }}
        }});
        
        // Followers Pie Chart
        var followersChart = echarts.init(document.getElementById('followersChart'));
        followersChart.setOption({{
            tooltip: {{ trigger: 'item', formatter: '{{b}}: {{c}} ({{d}}%)' }},
            series: [{{
                type: 'pie',
                radius: ['35%', '65%'],
                center: ['50%', '50%'],
                itemStyle: {{ borderRadius: 8, borderColor: '#1a1a2e', borderWidth: 2 }},
                label: {{ color: '#fff', fontSize: 11 }},
                data: {json.dumps([{'name': n, 'value': v} for n, v in zip(board_names, board_followers) if v > 0][:8])}
            }}]
        }});
        
        // Efficiency Chart
        var efficiencyChart = echarts.init(document.getElementById('efficiencyChart'));
        efficiencyChart.setOption({{
            tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'shadow' }} }},
            xAxis: {{
                type: 'value',
                axisLabel: {{ color: '#888' }},
                splitLine: {{ lineStyle: {{ color: 'rgba(255,255,255,0.1)' }} }}
            }},
            yAxis: {{
                type: 'category',
                data: {json.dumps([e['name'] for e in efficiency_data[:8]])},
                axisLabel: {{ color: '#888', fontSize: 11 }}
            }},
            series: [{{
                data: {json.dumps([e['value'] for e in efficiency_data[:8]])},
                type: 'bar',
                itemStyle: {{
                    color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                        {{ offset: 0, color: '#4ade80' }},
                        {{ offset: 1, color: '#22c55e' }}
                    ]),
                    borderRadius: [0, 4, 4, 0]
                }}
            }}],
            grid: {{ left: 120, right: 30, bottom: 20, top: 20 }}
        }});
        
        window.addEventListener('resize', () => {{
            pinsChart.resize();
            followersChart.resize();
            efficiencyChart.resize();
        }});
    </script>
</body>
</html>'''


def get_boards_page(data: dict) -> str:
    """Generate boards page HTML"""
    account = data.get('account', {})
    boards = data.get('boards', [])
    
    # Sort boards by pins
    boards_sorted = sorted(boards, key=lambda x: x.get('pin_count', 0) or 0, reverse=True)
    total_pins = sum(b.get('pin_count', 0) or 0 for b in boards)
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pinterest Analytics - Boards</title>
    <style>{get_base_styles()}</style>
</head>
<body>
    {get_nav_html('/boards', account.get('username', 'User'))}
    
    <main class="main">
        <h1 class="page-title">📋 All Boards <small>{len(boards)} boards • {total_pins:,} total pins</small></h1>
        
        <div class="table-card">
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Board Name</th>
                        <th>Pins</th>
                        <th>% of Total</th>
                        <th>Followers</th>
                        <th>Efficiency</th>
                        <th>Privacy</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f"""<tr>
                        <td>{i+1}</td>
                        <td><strong>{b.get('name', 'Unknown')}</strong></td>
                        <td>{b.get('pin_count', 0) or 0:,}</td>
                        <td>
                            <div style="display:flex;align-items:center;gap:10px">
                                <div class="progress" style="width:100px">
                                    <div class="progress-bar" style="width:{round((b.get('pin_count', 0) or 0) / max(total_pins, 1) * 100)}%"></div>
                                </div>
                                <span>{round((b.get('pin_count', 0) or 0) / max(total_pins, 1) * 100, 1)}%</span>
                            </div>
                        </td>
                        <td>{b.get('follower_count', 0) or 0:,}</td>
                        <td>{round((b.get('follower_count', 0) or 0) / max(b.get('pin_count', 0) or 1, 1), 2)}</td>
                        <td><span class="badge badge-{'success' if b.get('privacy') == 'PUBLIC' else 'warning'}">{b.get('privacy', 'PUBLIC')}</span></td>
                    </tr>""" for i, b in enumerate(boards_sorted)])}
                </tbody>
            </table>
        </div>
    </main>
    
    <footer class="footer">
        Pinterest Analytics Dashboard v2.0
    </footer>
</body>
</html>'''


def get_cleanup_page(data: dict) -> str:
    """Generate cleanup page HTML"""
    account = data.get('account', {})
    cleanup = data.get('cleanup', {})
    summary = cleanup.get('summary', {})
    by_board = cleanup.get('by_board', {})
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pinterest Analytics - Cleanup</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>{get_base_styles()}</style>
</head>
<body>
    {get_nav_html('/cleanup', account.get('username', 'User'))}
    
    <main class="main">
        <h1 class="page-title">🗑️ Cleanup Analysis <small>Find underperforming content</small></h1>
        
        <div class="alert alert-info">
            ℹ️ Run <code style="background:rgba(0,0,0,0.3);padding:2px 8px;border-radius:4px">python main.py cleanup</code> to analyze old pins
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="icon">📌</div>
                <div class="label">Total Pins</div>
                <div class="value">{summary.get('total_pins', 0):,}</div>
            </div>
            <div class="stat-card">
                <div class="icon">📅</div>
                <div class="label">Old Pins</div>
                <div class="value" style="color:var(--warning)">{summary.get('old_pins', 0):,}</div>
            </div>
            <div class="stat-card">
                <div class="icon">✨</div>
                <div class="label">New Pins (keep)</div>
                <div class="value" style="color:var(--success)">{summary.get('new_pins', 0):,}</div>
            </div>
            <div class="stat-card">
                <div class="icon">📊</div>
                <div class="label">% to Cleanup</div>
                <div class="value">{summary.get('percentage_old', 0)}%</div>
            </div>
        </div>
        
        <div class="charts-grid">
            <div class="chart-card">
                <h3>📊 Content Age Distribution</h3>
                <div id="ageChart" class="chart"></div>
            </div>
            <div class="chart-card">
                <h3>📋 Old Pins by Board</h3>
                <div id="boardCleanupChart" class="chart"></div>
            </div>
        </div>
        
        <div class="table-card">
            <h3>Top Boards with Old Content</h3>
            <table>
                <thead>
                    <tr>
                        <th>Board</th>
                        <th>Old Pins</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f"""<tr>
                        <td><strong>{board}</strong></td>
                        <td>{count:,}</td>
                        <td><span class="badge badge-{'danger' if count > 100 else 'warning' if count > 20 else 'success'}">{'High priority' if count > 100 else 'Medium' if count > 20 else 'Low'}</span></td>
                    </tr>""" for board, count in sorted(by_board.items(), key=lambda x: x[1], reverse=True)[:10]]) or '<tr><td colspan="3" style="color:#888;text-align:center">No cleanup data. Run: python main.py cleanup</td></tr>'}
                </tbody>
            </table>
        </div>
    </main>
    
    <footer class="footer">
        Pinterest Analytics Dashboard v2.0
    </footer>
    
    <script>
        // Age distribution chart
        var ageChart = echarts.init(document.getElementById('ageChart'));
        ageChart.setOption({{
            tooltip: {{ trigger: 'item' }},
            series: [{{
                type: 'pie',
                radius: ['40%', '70%'],
                data: [
                    {{ value: {summary.get('new_pins', 0)}, name: 'New (keep)', itemStyle: {{ color: '#4ade80' }} }},
                    {{ value: {summary.get('old_pins', 0)}, name: 'Old (cleanup)', itemStyle: {{ color: '#fbbf24' }} }}
                ],
                label: {{ color: '#fff' }}
            }}]
        }});
        
        // Board cleanup chart
        var boardData = {json.dumps([{'name': k[:15], 'value': v} for k, v in sorted(by_board.items(), key=lambda x: x[1], reverse=True)[:8]])};
        var boardCleanupChart = echarts.init(document.getElementById('boardCleanupChart'));
        boardCleanupChart.setOption({{
            tooltip: {{ trigger: 'axis' }},
            xAxis: {{
                type: 'category',
                data: boardData.map(d => d.name),
                axisLabel: {{ color: '#888', rotate: 45, fontSize: 11 }}
            }},
            yAxis: {{
                type: 'value',
                axisLabel: {{ color: '#888' }},
                splitLine: {{ lineStyle: {{ color: 'rgba(255,255,255,0.1)' }} }}
            }},
            series: [{{
                data: boardData.map(d => d.value),
                type: 'bar',
                itemStyle: {{
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        {{ offset: 0, color: '#fbbf24' }},
                        {{ offset: 1, color: '#f59e0b' }}
                    ]),
                    borderRadius: [6, 6, 0, 0]
                }}
            }}],
            grid: {{ left: 50, right: 20, bottom: 80, top: 20 }}
        }});
        
        window.addEventListener('resize', () => {{
            ageChart.resize();
            boardCleanupChart.resize();
        }});
    </script>
</body>
</html>'''


def get_keywords_page(data: dict) -> str:
    """Generate keywords page HTML"""
    account = data.get('account', {})
    keywords = data.get('keywords', {})
    top_keywords = keywords.get('top_keywords', [])
    recommendations = keywords.get('recommendations', [])
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pinterest Analytics - Keywords</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>{get_base_styles()}</style>
</head>
<body>
    {get_nav_html('/keywords', account.get('username', 'User'))}
    
    <main class="main">
        <h1 class="page-title">🔑 Keyword Analysis <small>SEO optimization for Pinterest</small></h1>
        
        <div class="alert alert-info">
            ℹ️ Run <code style="background:rgba(0,0,0,0.3);padding:2px 8px;border-radius:4px">python main.py keywords</code> to analyze your keywords
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="icon">📝</div>
                <div class="label">Pins Analyzed</div>
                <div class="value">{keywords.get('total_pins_analyzed', 0):,}</div>
            </div>
            <div class="stat-card">
                <div class="icon">🔤</div>
                <div class="label">Unique Keywords</div>
                <div class="value">{keywords.get('unique_keywords', 0):,}</div>
            </div>
            <div class="stat-card">
                <div class="icon">📊</div>
                <div class="label">Top Keyword</div>
                <div class="value" style="font-size:1.2rem">{top_keywords[0].get('keyword', 'N/A') if top_keywords else 'N/A'}</div>
            </div>
        </div>
        
        <div class="charts-grid">
            <div class="chart-card">
                <h3>📊 Top Keywords</h3>
                <div id="keywordsChart" class="chart chart-lg"></div>
            </div>
            <div class="chart-card">
                <h3>☁️ Keyword Cloud</h3>
                <div class="keyword-cloud" style="min-height:350px;align-content:flex-start">
                    {''.join([f'<span class="keyword-tag" style="font-size:{min(1.5, 0.8 + kw.get("frequency", 0) / 20)}rem">{kw.get("keyword", "")}<span class="count">({kw.get("count", 0)})</span></span>' for kw in top_keywords[:25]]) or '<span style="color:#888">No keywords data</span>'}
                </div>
            </div>
        </div>
        
        {f'''<div class="table-card">
            <h3>💡 SEO Recommendations</h3>
            <ul style="list-style:none;padding:0">
                {''.join([f'<li style="padding:12px 0;border-bottom:1px solid rgba(255,255,255,0.1);display:flex;align-items:center;gap:10px"><span style="color:var(--warning)">→</span> {rec}</li>' for rec in recommendations])}
            </ul>
        </div>''' if recommendations else ''}
    </main>
    
    <footer class="footer">
        Pinterest Analytics Dashboard v2.0
    </footer>
    
    <script>
        var keywordsData = {json.dumps(top_keywords[:15])};
        var keywordsChart = echarts.init(document.getElementById('keywordsChart'));
        keywordsChart.setOption({{
            tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'shadow' }} }},
            xAxis: {{
                type: 'value',
                axisLabel: {{ color: '#888' }},
                splitLine: {{ lineStyle: {{ color: 'rgba(255,255,255,0.1)' }} }}
            }},
            yAxis: {{
                type: 'category',
                data: keywordsData.map(k => k.keyword).reverse(),
                axisLabel: {{ color: '#888', fontSize: 11 }}
            }},
            series: [{{
                data: keywordsData.map(k => k.count).reverse(),
                type: 'bar',
                itemStyle: {{
                    color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                        {{ offset: 0, color: '#E60023' }},
                        {{ offset: 1, color: '#ff6b6b' }}
                    ]),
                    borderRadius: [0, 4, 4, 0]
                }}
            }}],
            grid: {{ left: 100, right: 30, bottom: 20, top: 20 }}
        }});
        
        window.addEventListener('resize', () => keywordsChart.resize());
    </script>
</body>
</html>'''


def get_trends_page(data: dict) -> str:
    """Generate trends page HTML"""
    account = data.get('account', {})
    trends = data.get('trends', {})
    boards_analysis = trends.get('boards', {})
    niche = trends.get('niche', {})
    patterns = trends.get('posting_patterns', {})
    
    most_efficient = boards_analysis.get('most_efficient', [])
    recommendations = boards_analysis.get('recommendations', [])
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pinterest Analytics - Trends</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>{get_base_styles()}</style>
</head>
<body>
    {get_nav_html('/trends', account.get('username', 'User'))}
    
    <main class="main">
        <h1 class="page-title">📈 Trends & Niche <small>Find what works for you</small></h1>
        
        <div class="alert alert-info">
            ℹ️ Run <code style="background:rgba(0,0,0,0.3);padding:2px 8px;border-radius:4px">python main.py trends --full</code> for complete analysis
        </div>
        
        {f'''<div class="alert alert-success">
            🎯 <strong>Your Niche:</strong> {niche.get('top_board_niche', 'Unknown')}
        </div>''' if niche.get('top_board_niche') else ''}
        
        <div class="charts-grid">
            <div class="chart-card">
                <h3>⚡ Most Efficient Boards <small style="color:#888;font-weight:normal">(followers per pin)</small></h3>
                <div id="efficiencyChart" class="chart"></div>
            </div>
            <div class="chart-card">
                <h3>📅 Best Posting Days</h3>
                <div id="daysChart" class="chart"></div>
            </div>
        </div>
        
        <div class="table-card">
            <h3>💡 Recommendations</h3>
            <ul style="list-style:none;padding:0">
                {''.join([f'<li style="padding:12px 0;border-bottom:1px solid rgba(255,255,255,0.1);display:flex;align-items:center;gap:10px"><span style="color:var(--success)">✓</span> {rec}</li>' for rec in recommendations]) or '<li style="color:#888">Run trends analysis to get recommendations</li>'}
            </ul>
        </div>
        
        <div class="table-card">
            <h3>🏆 Most Efficient Boards</h3>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Board</th>
                        <th>Pins</th>
                        <th>Followers</th>
                        <th>Efficiency</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f"""<tr>
                        <td>{i+1}</td>
                        <td><strong>{b.get('name', 'Unknown')}</strong></td>
                        <td>{b.get('pins', 0):,}</td>
                        <td>{b.get('followers', 0):,}</td>
                        <td><span class="badge badge-success">{b.get('efficiency', 0)}</span></td>
                    </tr>""" for i, b in enumerate(most_efficient[:10])]) or '<tr><td colspan="5" style="color:#888;text-align:center">Run: python main.py trends</td></tr>'}
                </tbody>
            </table>
        </div>
    </main>
    
    <footer class="footer">
        Pinterest Analytics Dashboard v2.0
    </footer>
    
    <script>
        // Efficiency chart
        var effData = {json.dumps(most_efficient[:8])};
        var efficiencyChart = echarts.init(document.getElementById('efficiencyChart'));
        efficiencyChart.setOption({{
            tooltip: {{ trigger: 'axis' }},
            xAxis: {{
                type: 'category',
                data: effData.map(e => (e.name || '').substring(0, 12)),
                axisLabel: {{ color: '#888', rotate: 45, fontSize: 11 }}
            }},
            yAxis: {{
                type: 'value',
                axisLabel: {{ color: '#888' }},
                splitLine: {{ lineStyle: {{ color: 'rgba(255,255,255,0.1)' }} }}
            }},
            series: [{{
                data: effData.map(e => e.efficiency || 0),
                type: 'bar',
                itemStyle: {{
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        {{ offset: 0, color: '#4ade80' }},
                        {{ offset: 1, color: '#22c55e' }}
                    ]),
                    borderRadius: [6, 6, 0, 0]
                }}
            }}],
            grid: {{ left: 50, right: 20, bottom: 80, top: 20 }}
        }});
        
        // Days chart
        var daysData = {json.dumps(patterns.get('by_day', {}))};
        var daysChart = echarts.init(document.getElementById('daysChart'));
        daysChart.setOption({{
            tooltip: {{ trigger: 'axis' }},
            xAxis: {{
                type: 'category',
                data: Object.keys(daysData),
                axisLabel: {{ color: '#888' }}
            }},
            yAxis: {{
                type: 'value',
                axisLabel: {{ color: '#888' }},
                splitLine: {{ lineStyle: {{ color: 'rgba(255,255,255,0.1)' }} }}
            }},
            series: [{{
                data: Object.values(daysData),
                type: 'line',
                smooth: true,
                areaStyle: {{
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        {{ offset: 0, color: 'rgba(230,0,35,0.5)' }},
                        {{ offset: 1, color: 'rgba(230,0,35,0)' }}
                    ])
                }},
                lineStyle: {{ color: '#E60023', width: 3 }},
                itemStyle: {{ color: '#E60023' }}
            }}],
            grid: {{ left: 50, right: 20, bottom: 30, top: 20 }}
        }});
        
        window.addEventListener('resize', () => {{
            efficiencyChart.resize();
            daysChart.resize();
        }});
    </script>
</body>
</html>'''


class DashboardHandler(SimpleHTTPRequestHandler):
    """Enhanced dashboard handler with routing"""
    
    dashboard_data = {}
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        if path == '/' or path == '/index.html':
            html = get_overview_page(self.dashboard_data)
        elif path == '/boards':
            html = get_boards_page(self.dashboard_data)
        elif path == '/cleanup':
            html = get_cleanup_page(self.dashboard_data)
        elif path == '/keywords':
            html = get_keywords_page(self.dashboard_data)
        elif path == '/trends':
            html = get_trends_page(self.dashboard_data)
        elif path == '/api/data':
            self.send_header('Content-type', 'application/json')
            self.wfile.write(json.dumps(self.dashboard_data, default=str).encode())
            return
        else:
            html = get_overview_page(self.dashboard_data)
        
        self.wfile.write(html.encode('utf-8'))
    
    def log_message(self, format, *args):
        pass


def start_dashboard(analytics, port: int = PORT):
    """Start the enhanced dashboard server"""
    print("Fetching data for dashboard...")
    
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
            'keywords': {},
            'cleanup': {'summary': {}, 'by_board': {}},
            'trends': {'boards': {}, 'niche': {}, 'posting_patterns': {}},
            'alerts': [],
        }
        
        # Try to load additional data
        try:
            from .keywords import get_keyword_analyzer
            keywords = get_keyword_analyzer().analyze_my_keywords()
            data['keywords'] = keywords
        except:
            pass
        
        try:
            from .bulk_analyzer import get_bulk_analyzer
            cleanup = get_bulk_analyzer().find_underperforming()
            data['cleanup'] = cleanup
        except:
            pass
        
        try:
            from .trends_analyzer import get_trends_analyzer
            trends = get_trends_analyzer().generate_trends_report()
            data['trends'] = trends
        except:
            pass
        
        DashboardHandler.dashboard_data = data
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        DashboardHandler.dashboard_data = {
            'account': {'username': 'Error'},
            'boards': [],
            'metrics': {},
            'alerts': [{'type': 'WARNING', 'message': str(e)}],
        }
    
    server = HTTPServer(('localhost', port), DashboardHandler)
    
    print(f"\n{'='*50}")
    print(f"Dashboard v2.0 running at: http://localhost:{port}")
    print(f"{'='*50}")
    print("Pages: Overview | Boards | Cleanup | Keywords | Trends")
    print("Press Ctrl+C to stop\n")
    
    webbrowser.open(f'http://localhost:{port}')
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping dashboard...")
        server.shutdown()


if __name__ == '__main__':
    from analytics import get_analytics
    start_dashboard(get_analytics())
