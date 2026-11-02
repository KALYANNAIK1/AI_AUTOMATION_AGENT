TEST_AUTOMATION_PROMPT = """
Analyze the requirement.

Requirement:
{requirement}

Generate:

1. Test Scenarios

2. Detailed Test Cases
   - TC ID
   - Summary
   - Priority
   - Steps
   - Actual Result
   - Expected Result

3. Playwright Page Object
   LoginPage.ts

4. Playwright Test Script
   login.spec.ts

Return sections separately.

Format Response:

===************ TEST SCENARIOS ************===

===************ TEST CASES ************===

===************ PAGE OBJECT ************===

===************ PLAYWRIGHT SCRIPT ************===
"""