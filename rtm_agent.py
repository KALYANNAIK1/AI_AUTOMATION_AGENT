import json
from pathlib import Path


class RTMAgent:

    def generate_rtm(
        self,
        requirements,
        scenarios,
        testcases
    ):

        rtm = []

        scenario_map = {}

        testcase_map = {}

        # Build Scenario Map

        for scenario in scenarios:

            scenario_id = scenario.get(
                "scenario_id",
                ""
            )

            scenario_map[
                scenario_id
            ] = scenario

        # Build Test Case Map

        for testcase in testcases:

            scenario_id = testcase.get(
                "scenario_id",
                ""
            )

            if scenario_id not in testcase_map:

                testcase_map[
                    scenario_id
                ] = []

            testcase_map[
                scenario_id
            ].append(testcase)

        # Generate RTM

        for req in requirements:

            requirement_id = req.get(
                "requirement_id",
                ""
            )

            requirement_name = req.get(
                "requirement",
                ""
            )

            scenario_id = req.get(
                "scenario_id",
                ""
            )

            related_testcases = (
                testcase_map.get(
                    scenario_id,
                    []
                )
            )

            rtm.append({

                "requirement_id":
                    requirement_id,

                "requirement":
                    requirement_name,

                "scenario_id":
                    scenario_id,

                "testcases": [
                    tc.get(
                        "tc_id"
                    )
                    for tc
                    in related_testcases
                ]
            })

        return rtm

    def save_rtm(
        self,
        rtm_data,
        output_file
    ):

        output_path = Path(
            output_file
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                rtm_data,
                file,
                indent=4
            )

        return str(output_path)