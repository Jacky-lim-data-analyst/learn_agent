from .basic_llm import BasicAgentsLLM
from prompts import PLANNER_PROMPT_TEMPLATE, EXECUTOR_PROMPT_TEMPLATE
from dotenv import load_dotenv
import ast

load_dotenv()

class Planner:
    def __init__(self, llm_client: BasicAgentsLLM) -> None:
        self.llm_client = llm_client

    def plan(self, question: str) -> list[str]:
        """
        Generate an action plan based on user question.
        """
        prompt = PLANNER_PROMPT_TEMPLATE.format(question=question)

        # to generate a plan, we build a simple message list
        messages = [{"role": "user", "content": prompt}]

        print("--- Generating Plan ---")
        # use streaming output to get the complete plan
        response_text = self.llm_client.think(messages=messages) or ""

        print(f"✅ Plan Generated:\n{response_text}")

        # Parse the list string output by LLM
        try:
            # find the content between ```python and ```
            plan_str = response_text.split("```python")[1].split("```")[0].strip()
            # Use ast.literal_eval to safely execute the string and convert it to a Python list
            plan = ast.literal_eval(plan_str)
            return plan if isinstance(plan, list) else []
        except (ValueError, SyntaxError, IndexError) as e:
            print(f"❌ Error parsing plan: {e}")
            print(f"Raw response: {response_text}")
            return []
        except Exception as e:
            print(f"❌ Unknown error occurred while parsing plan: {e}")
            return []
        
class Executor:
    def __init__(self, llm_client: BasicAgentsLLM):
        self.llm_client = llm_client

    def execute(self, question: str, plan: list[str]) -> str:
        """
        Execute step by step according to the plan and solve the problem.
        """
        history = ""

        print("\n--- Executing plan ---")

        for i, step in enumerate(plan):
            print(f"\n-> Executing step [{i+1}]/[{len(plan)}]: {step}")

            prompt = EXECUTOR_PROMPT_TEMPLATE.format(
                question=question,
                plan=plan,
                history=history if history else "None",
                current_step=step
            )

            messages = [{"role": "user", "content": prompt}]

            response_text = self.llm_client.think(messages=messages) or ""

            # update history
            history += f"Step {i+1}: {step}\nResult: {response_text}\n\n"

            print(f"✅ Step {i+1} completed, result: {response_text}")
            final_answer = response_text

        # after the loop ends, the last step's response is the final answer
        return final_answer
    
class PlanAndSolveAgent:
    def __init__(self, llm_client: BasicAgentsLLM) -> None:
        self.llm_client = llm_client
        self.planner = Planner(self.llm_client)
        self.executor = Executor(self.llm_client)

    def run(self, question: str):
        """
        Run the agent's complete process: plan first, then execute.
        """
        print(f"\n--- Starting to process Question ---\nQuestion: {question}")

        # 1. call planner to generate plan
        plan = self.planner.plan(question)

        # check if plan was successfully generated
        if not plan:
            print("\n--- Task Terminated --- \nUnable to generate valid action plan.")
            return
        
        # 2 call executor
        final_answer = self.executor.execute(question, plan)

        print(f"\n--- Task completed --- \n Final answer: {final_answer}")

if __name__ == "__main__":
    try:
        llm_client = BasicAgentsLLM()
        agent = PlanAndSolveAgent(llm_client)
        question = "A fruit store sold 15 apples on Monday. The number of apples sold on Tuesday was twice that of Monday. The number sold on Wednesday was 5 fewer than Tuesday. How many apples were sold in total over these three days?"
        agent.run(question=question)
    except ValueError as e:
        print(e)
    except Exception as e:
        print(f"Unexpected error: {e}")
        