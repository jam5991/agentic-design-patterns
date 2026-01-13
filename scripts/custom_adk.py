import os
from typing import List, Callable, Any, Dict, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import Tool, tool
from pydantic import BaseModel, ConfigDict

@tool
def google_search(query: str) -> str:
    """
    Performs a Google Search for the given query.
    """
    # In a real scenario, this would call the Google Search API.
    # For this book example, we return simulated results.
    return f"Simulated Search Result for '{query}': Found relevant information about the topic."


class Agent(BaseModel):
    name: str
    model: str
    instruction: str
    tools: List[Any] = []
    callbacks: List[Callable] = []
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the agent logic.
        This is a simplified implementation for demonstration purposes.
        """
        print(f"\n[Agent: {self.name}] Running...")
        
        # Initialize LLM
        llm = ChatGoogleGenerativeAI(model=self.model, temperature=0)
        
        # Bind tools
        llm_with_tools = llm.bind_tools(self.tools) if self.tools else llm
        
        # Construct messages
        # We assume the state contains a "messages" key or we construct one from specific keys
        # For this specific pattern (primary/fallback), we'll look at the specific logic needed.
        # But to be generic-ish:
        
        messages = [SystemMessage(content=self.instruction)]
        
        # Add context from state
        state_desc = f"Current State: {state}"
        messages.append(HumanMessage(content=state_desc))
        
        # Execute callbacks (allow them to modify messages)
        for callback in self.callbacks:
            callback(self, messages, state)
        
        try:
            response = llm_with_tools.invoke(messages)
            print(f"[Agent: {self.name}] Response: {response.content}")
            
            # Simple tool execution logic if tool_calls exist
            if hasattr(response, 'tool_calls') and response.tool_calls:
                for tool_call in response.tool_calls:
                    tool_name = tool_call['name']
                    tool_args = tool_call['args']
                    print(f"[Agent: {self.name}] Calling tool: {tool_name} with {tool_args}")
                    
                    # Find tool
                    tool_func = next((t for t in self.tools if t.name == tool_name), None)
                    if tool_func:
                        # Invoke tool
                        if hasattr(tool_func, 'invoke'):
                            result = tool_func.invoke(tool_args)
                        else:
                            # Fallback for simple functions
                            result = tool_func(**tool_args)
                            
                        print(f"[Agent: {self.name}] Tool Result: {result}")
                        
                        # Update state based on tool result
                        # Generic update:
                        state.setdefault("tool_outputs", {})[tool_name] = result
                        
                        # Specific logic for Chapter 12 (Error Handling) preservation
                        if tool_name == 'get_precise_location_info':
                            if result:
                                state["location_result"] = result
                                state["primary_location_failed"] = False
                            else:
                                state["primary_location_failed"] = True
                        elif tool_name == 'get_general_area_info':
                            state["location_result"] = result
                            
                        # Specific logic for Chapter 13 (HITL)
                        if tool_name in ['troubleshoot_issue', 'create_ticket', 'escalate_to_human']:
                            # Store the last action result to be picked up if needed
                            state["last_action_result"] = result
            
        except Exception as e:
            print(f"[Agent: {self.name}] Error: {e}")
            # Ensure state reflects failure if meaningful
            if self.name == "primary_handler":
                state["primary_location_failed"] = True
                
        return state

class SequentialAgent:
    def __init__(self, name: str, sub_agents: List[Agent]):
        self.name = name
        self.sub_agents = sub_agents

    def run(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        print(f"Starting Sequential Workflow: {self.name}")
        current_state = initial_state.copy()
        for agent in self.sub_agents:
            current_state = agent.run(current_state)
        return current_state
