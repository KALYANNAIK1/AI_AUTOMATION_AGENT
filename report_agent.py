from datetime import datetime


class ReportAgent:

    def generate_report(
        self,
        execution_result
    ):

        report = {
            "execution_date":
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

            "status":
                execution_result.get(
                    "status",
                    "UNKNOWN"
                ),

            "returncode":
                execution_result.get(
                    "returncode",
                    -1
                ),

            "command":
                execution_result.get(
                    "command",
                    ""
                ),

            "stdout":
                execution_result.get(
                    "stdout",
                    ""
                ),

            "stderr":
                execution_result.get(
                    "stderr",
                    ""
                )
        }

        return report

    def generate_html_report(
        self,
        report
    ):

        html = f"""
<!DOCTYPE html>
<html>
<head>
<title>Execution Report</title>
<style>

body {{
    font-family: Arial, sans-serif;
    margin: 20px;
}}

table {{
    border-collapse: collapse;
    width: 100%;
}}

td, th {{
    border: 1px solid #dddddd;
    text-align: left;
    padding: 8px;
}}

.success {{
    color: green;
    font-weight: bold;
}}

.failed {{
    color: red;
    font-weight: bold;
}}

</style>
</head>
<body>

<h1>Automation Execution Report</h1>

<table>

<tr>
<th>Execution Date</th>
<td>{report['execution_date']}</td>
</tr>

<tr>
<th>Status</th>
<td>
{report['status']}
</td>
</tr>

<tr>
<th>Return Code</th>
<td>{report['returncode']}</td>
</tr>

</table>

<h2>Stdout</h2>

<pre>
{report['stdout']}
</pre>

<h2>Stderr</h2>

<pre>
{report['stderr']}
</pre>

</body>
</html>
"""

        return html