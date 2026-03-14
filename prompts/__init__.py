# ReAct Prompt Template
REACT_PROMPT_TEMPLATE = """
Please note that you are an intelligent assistant capable of calling external tools.

Available tools are as follows:
{tools}

Please respond strictly in the following format:

Thought: Your thinking process, used to analyze problems, decompose tasks, and plan the next action.
Action: The action you decide to take, must be in one of the following formats:
- {{tool_name}}[{{tool_input}}]`: Call an available tool.
- `Finish[final answer]`: When you believe you have obtained the final answer.
- When you have collected enough information to answer the user's final question, you must use `Finish[final answer]` after the Action: field to output the final answer.

Now, please start solving the following problem:
Question: {question}
History: {history}
"""

PLANNER_PROMPT_TEMPLATE = """
You are a top AI planning expert. Your task is to decompose complex problems posed by users into an action plan consisting of multiple simple steps.
Please ensure that each step in the plan is an independent, executable subtask and is strictly arranged in logical order.
Your output must be a Python list, where each element is a string describing a subtask.

Question: {question}

Please strictly output your plan in the following format, with ```python and ``` as prefix and suffix being necessary:
```python
["Step 1", "Step 2", "Step 3", ...]
```
"""

EXECUTOR_PROMPT_TEMPLATE = """
You are a top AI execution expert. Your task is to strictly follow the given plan and solve the problem step by step.
You will receive the original question, the complete plan, and the steps and results completed so far.
Please focus on solving the "current step" and only output the final answer for that step, without any additional explanations or dialogue.

# Original Question:
{question}

# Complete Plan:
{plan}

# Historical Steps and Results:
{history}

# Current Step:
{current_step}

Please only output the answer for the "current step":
"""

# ---- Reflection agent ---
INITIAL_PROMPT_TEMPLATE = """
You are a senior Python programmer. Please write a Python function according to the following requirements.
Your code must include a complete function signature, docstring, and follow PEP 8 coding standards.

Requirement: {task}

Please output the code directly without any additional explanations.
"""

REFLECT_PROMPT_TEMPLATE = """
You are an extremely strict code review expert and senior algorithm engineer with ultimate requirements for code performance.
Your task is to review the following Python code and focus on finding its main bottlenecks in <strong>algorithm efficiency</strong>.

# Original Task:
{task}

# Code to Review:
```python
{code}
```

Please analyze the time complexity of this code and consider whether there is an <strong>algorithmically superior</strong> solution to significantly improve performance.
If one exists, please clearly point out the deficiencies of the current algorithm and propose specific, feasible algorithm improvement suggestions (e.g., using sieve method instead of trial division).
Only if the code has reached optimality at the algorithm level can you answer "no improvement needed."

Please output your feedback directly without any additional explanations.
"""


REFINE_PROMPT_TEMPLATE = """
You are a senior Python programmer. You are optimizing your code based on feedback from a code review expert.

# Original Task:
{task}

# Your Previous Code Attempt:
{last_code_attempt}
Reviewer's Feedback:
{feedback}

Please generate an optimized new version of the code based on the reviewer's feedback.
Your code must include a complete function signature, docstring, and follow PEP 8 coding standards.
Please output the optimized code directly without any additional explanations.
"""
