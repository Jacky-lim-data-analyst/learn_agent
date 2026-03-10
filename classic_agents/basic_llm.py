import os
import re
from openai import OpenAI
from dotenv import load_dotenv
from tools.base import ToolExecutor
from tools.web_search import search
from prompts import REACT_PROMPT_TEMPLATE

# load environment variables from .env file
load_dotenv()

class BasicAgentsLLM:
    """This class is used to call any service compatible with the OpenAI interface and uses streaming responses by default."""
    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        max_retries: int = 3) -> None:
        """
        Initialize the client. Prioritize passed parameters; if not provided, load from environment variables.
        """
        self.model = model or os.getenv("LLM_MODEL_ID")
        api_key = api_key or os.getenv("LLM_API_KEY")
        base_url = base_url or os.getenv("LLM_BASE_URL")

        if not all([self.model, api_key, base_url]):
            raise ValueError("Model name, api key and base url are required.")
        
        self.client = OpenAI(api_key=api_key, base_url=base_url, max_retries=max_retries)

    def think(self, messages: list[dict[str, str]], temperature: float = 0.1) -> str | None:
        """
        Call the large language model to think and return its response.
        """
        print(f"🤖 Calling {self.model} model...")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=True
            )

            print("LLM response successful")
            collected_content = []
            for chunk in response:
                if not chunk.choices[0]:
                    continue
                content = chunk.choices[0].delta.content or ""
                print(content, end="", flush=True)
                collected_content.append(content)

            print()
            return "".join(collected_content)
        except Exception as exc:
            print(f"❌ Error occurred when calling LLM API: {exc}")
            return None
        
class ReActAgent:
    def __init__(self, llm_client: BasicAgentsLLM, tool_executor: ToolExecutor, max_steps: int = 5):
        self.llm_client = llm_client
        self.tool_executor = tool_executor
        self.max_steps = max_steps
        self.history = []

    def run(self, question: str):
        """
        Run the ReAct agent to answer a question.
        """
        self.history = []   # reset history for each run
        current_step = 0

        while current_step < self.max_steps:
            current_step += 1
            print(f"--- Step {current_step} ---")

            # format prompt
            tools_desc = self.tool_executor.get_available_tools()
            history_str = "\n".join(self.history)
            prompt = REACT_PROMPT_TEMPLATE.format(
                tools=tools_desc,
                question=question,
                history=history_str
            )

            # call LLM to think
            messages = [{"role": "user", "content": prompt}]
            response_text = self.llm_client.think(messages=messages)

            if not response_text:
                print("Error: LLM failed to return a valid response")
                break

            # parse LLM output
            thought, action = self._parse_output(response_text)

            if thought:
                print(f"Thought: {thought}")

            if not action:
                print("Warning: Failed to parse valid action, process terminated")
                break

            # 4 execute action
            if action.startswith("Finish"):
                # final answer found
                final_answer = re.match(r"Finish\[(.*)\]", action).group(1)
                print(f"🎉 Final Answer: {final_answer}")
                return final_answer
            
            tool_name, tool_input = self._parse_action(action)

            if not tool_name or not tool_input:
                continue

            print(f"🎬 Action: {tool_name}[{tool_input}]")

            tool_function = self.tool_executor.get_tool(tool_name)
            if not tool_function:
                observation = f"Error: Tool named '{tool_name}' not found."
            else:
                observation = tool_function(tool_input)

            print(f"👀 Observation: {observation}")
            self.history.append(f"Action: {action}")
            self.history.append(f"Observation: {observation}")

        # Loop ends
        print("Maximum steps reached, process terminated.")
        return None

    def _parse_output(self, text: str):
        """Parse LLM output to extract thought and action"""
        # thought
        thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|$)", text, re.DOTALL)
        # action
        action_match = re.search(r"Action:\s*(.*?)$", text, re.DOTALL)
        thought = thought_match.group(1).strip() if thought_match else None
        action = action_match.group(1).strip() if action_match else None
        return thought, action
    
    def _parse_action(self, action_text: str):
        """Parse Action string to extract tool name and input.
        """
        match = re.match(r"(\w+)\[(.*)\]", action_text, re.DOTALL)
        if match:
            return match.group(1), match.group(2)
        return None, None
        
if __name__ == "__main__":
    # try:
    #     llmClient = BasicAgentsLLM()

    #     exampleMessages = [
    #         {
    #             "role": "system", "content": "You are a helpful assistant in Python codes writing",
    #         },
    #         {
    #             "role": "user", "content": "Write a quicksort algorithm"
    #         }
    #     ]

    #     response = llmClient.think(exampleMessages)
    #     if response:
    #         print(response)
    # except ValueError as e:
    #     print(e)
    llm = BasicAgentsLLM()
    tool_executor = ToolExecutor()
    search_description = (
        "A web search engine. Use this tool when you need to answer questions about "
        "current events, facts, and information not found in your knowledge base."
    )
    tool_executor.register_tool("Search", description=search_description, func=search)

    agent = ReActAgent(llm_client=llm, tool_executor=tool_executor)

    question = "What is Moltbook?"
    agent.run(question=question)
        