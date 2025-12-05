# MissionSmith Story Execution Loop

1. Select the next Story from the sequencing list:
   - docs/mission_destination/initial_story_sequence.md

2. Identify the service for the Story:
   - Add or update the entry for the Story in story_service_mapping.yaml to record the service and the code file to be updated.

3. Implement the Story using the code meta-prompt:
   - story_code_instruction_prompt_template.txt
   - story_code_metaprompt.md

4. Create the tests using the test meta-prompt:
   - story_test_instruction_prompt_template.txt
   - story_test_metaprompt.md

5. Update the Story → Service mapping in the automation scripts using:
   - generate_story_config_snippets.py
   Then paste outputs into:
   - run_story_tests.py
   - run_story_lint.py
   - run_story_security.py
   - run_story_guardrails.py

6. Run the status update scripts:
   - python tools/run_story_tests.py ST-XX
   - python tools/run_story_lint.py ST-XX
   - python tools/run_story_security.py ST-XX
   - python tools/run_story_guardrails.py ST-XX

