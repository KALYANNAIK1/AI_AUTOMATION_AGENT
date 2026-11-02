from datetime import datetime


class JiraAgent:

    def create_defect(
        self,
        summary,
        description,
        severity="Medium"
    ):

        jira_ticket = {

            "IssueKey": "AUTO-101",

            "Summary": summary,

            "Description": description,

            "Severity": severity,

            "CreatedDate":
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

            "Status": "Created"
        }

        return jira_ticket