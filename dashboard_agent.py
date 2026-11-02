from datetime import datetime
from pathlib import Path
import json


class DashboardAgent:

    def generate_dashboard(
        self,
        feature_name,
        report,
        output_dir="generated/dashboard"
    ):

        Path(output_dir).mkdir(
            parents=True,
            exist_ok=True
        )

        status = report.get(
            "status",
            "UNKNOWN"
        )

        status_color = (
            "green"
            if status == "SUCCESS"
            else "red"
        )

        html = f"""
<!DOCTYPE html>
<html>

<head>

<title>AI Automation Dashboard</title>

<style>

body {{
    font-family: Arial, sans-serif;
    margin: 20px;
    background-color: #f5f5f5;
}}

.header {{
    background-color: #0078D4;
    color: white;
    padding: 15px;
    border-radius: 5px;
}}

.card {{
    background-color: white;
    padding: 20px;
    margin-top: 20px;
    border-radius: 5px;
    box-shadow: 0px 2px 5px rgba(0,0,0,0.1);
}}

.status {{
    color: {status_color};
    font-weight: bold;
}}

pre {{
    background-color: #f0f0f0;
    padding: 10px;
    overflow-x: auto;
}}

</style>

</head>

<body>

<div class="header">
<h1>AI Automation Dashboard</h1>
</div>

<div class="card">
<h2>Feature</h2>
<p>{feature_name}</p>
</div>

<div class="card">
<h2>Execution Summary</h2>

<p>
Status:
<span class="status">
{status}
</span>
</p>

<p>
Execution Time:
{datetime.now()}
</p>

<p>
Return Code:
{report.get('returncode')}
</p>

</div>

<div class="card">
<h2>Execution Output</h2>

<pre>
{report.get('stdout', '')}
</pre>

</div>

<div class="card">
<h2>Error Log</h2>

<pre>
{report.get('stderr', '')}
</pre>

</div>

</body>
</html>
"""

        dashboard_path = (
            Path(output_dir)
            / "dashboard.html"
        )

        dashboard_path.write_text(
            html,
            encoding="utf-8"
        )

        return str(dashboard_path)