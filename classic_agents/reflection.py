from typing import List, Dict, Any

from .basic_llm import BasicAgentsLLM
from prompts import (
    INITIAL_PROMPT_TEMPLATE,
    REFLECT_PROMPT_TEMPLATE,
    REFINE_PROMPT_TEMPLATE
)

class Memory:
    """
    A simple short-term memory module for storing the agent's action and reflection trajectory.
    """
    def __init__(self):
        """Initialize an empty list to store all records"""
        self.records: List[Dict[str, Any]] = []

    def add_record(self, record_type: str, content: str):
        """Add a new record to memory.

        Parameters:
        - record_type (str): Type of record ('execution' or 'reflection').
        - content (str): Specific content of the record (e.g., generated code or reflection feedback)."""
        record = {"type": record_type, "content": content}
        self.records.append(record)
        print(f"📝 Memory updated, added a '{record_type}' record.")

    def get_trajectory(self) -> str:
        """
        Format all memory records into a coherent string text for building prompts.
        """
        trajectory_parts = []
        for record in self.records:
            if record["type"] == "execution":
                trajectory_parts.append(f"--- Previous attempt (Code) ---\n{record['content']}")
            elif record["type"] == "reflection":
                trajectory_parts.append(f"--- Reviewer Feedback ---\n{record['content']}")

        return "\n\n".join(trajectory_parts)
    
    def get_last_execution(self) -> str | None:
        """
        Get the most recent execution result (e.g., the latest generated code).
        Returns None if it doesn't exist.
        """
        for record in reversed(self.records):
            if record['type'] == 'execution':
                return record['content']
        return None
    
class ReflectionAgent:
    def __init__(self, llm_client: BasicAgentsLLM, max_iterations: int = 3) -> None:
        self.llm_client = llm_client
        self.memory = Memory()
        self.max_iterations = max_iterations
    
    def _get_llm_response(self, prompt: str) -> str:
        """A helper method for calling LLM and getting complete streaming response"""
        messages = [{"role": "user", "content": prompt}]
        response_text = self.llm_client.think(messages=messages) or ""
        return response_text

    def run(self, task: str):
        print(f"\n--- Starting to Process task ---\nTask: {task}")

        # --- 1. Initial execution ---
        initial_prompt = INITIAL_PROMPT_TEMPLATE.format(task=task)
        initial_code = self._get_llm_response(initial_prompt)
        self.memory.add_record(record_type="execution", content=initial_code)

        # --- 2. Iterative loop: Reflection and Refinement ---
        for i in range(self.max_iterations):
            print(f"\n--- Iteration {i+1}/{self.max_iterations} ---")

            # reflection
            print("\n--- Performing Reflection ---")
            last_code = self.memory.get_last_execution()
            reflect_prompt = REFLECT_PROMPT_TEMPLATE.format(task=task, code=last_code)
            feedback = self._get_llm_response(reflect_prompt)
            self.memory.add_record("reflection", feedback)

            # check if stopping condition met
            if "no improvement needed" in feedback.lower():
                print("\n✅ Reflection considers code needs no improvement, task completed.")
                break

            # refinement
            print("\n-> Performing Refinement...")
            refine_prompt = REFINE_PROMPT_TEMPLATE.format(
                task=task,
                last_code_attempt=last_code,
                feedback=feedback
            )
            refined_code = self._get_llm_response(refine_prompt)
            self.memory.add_record("execution", refined_code)

        final_code = self.memory.get_last_execution()
        print(f"\n--- Task Completed ---\nFinal Generated Code:\n```python\n{final_code}\n```")
        return final_code
    
if __name__ == "__main__":
    llm_client = BasicAgentsLLM()

    agent = ReflectionAgent(llm_client=llm_client, max_iterations=2)

    task = "Write a Python function to find prime numbers from 1 to n"
    agent.run(task)
    