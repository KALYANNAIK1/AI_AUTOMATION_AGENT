from pathlib import Path

import pandas as pd


class ExcelAgent:

    def __init__(self):
        self.output_dir = Path(__file__).resolve().parent / "generated" / "exports"

    def _save(self, filename, rows):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        file_path = self.output_dir / filename
        pd.DataFrame(rows).to_excel(file_path, index=False)
        return str(file_path)

    def save_requirements(
            self,
            requirement):
        return self._save("Requirements.xlsx", [{"Requirement": requirement}])

    def save_scenarios(
            self,
            scenarios):
        rows = (
            [{"Scenario": scenario} for scenario in scenarios]
            if isinstance(scenarios, (list, tuple))
            else [{"Scenarios": scenarios}]
        )
        return self._save("Scenarios.xlsx", rows)

    def save_testcases(
            self,
            testcases):
        if isinstance(testcases, (list, tuple)):
            rows = [
                testcase if isinstance(testcase, dict) else {"TestCase": testcase}
                for testcase in testcases
            ]
        else:
            rows = [{"TestCases": testcases}]
        return self._save("TestCases.xlsx", rows)