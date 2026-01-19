"""
Advanced Reasoning Patterns with LangGraph
Demonstrates multi-agent reasoning with state management and conditional logic.
"""
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool
from google.adk.code_executors import BuiltInCodeExecutor


class OverallState(TypedDict):
    """State management for the reasoning graph"""
    query: str
    search_results: List[str]
    reflections: List[str]
    final_answer: str
    iteration_count: int
    quality_score: float


class ReasoningGraph:
    """Advanced reasoning graph with multiple agents and conditional logic"""
    
    def __init__(self):
        # Create specialized agents
        self.search_agent = LlmAgent(
            model='gemini-2.5-flash',
            name='SearchAgent',
            description="Specialist in web searching and information gathering",
            instruction="You're a specialist in finding and summarizing relevant information. Be thorough and accurate."
        )
        
        self.coding_agent = LlmAgent(
            model='gemini-2.5-flash',
            name='CodeAgent',
            description="Specialist in code execution and analysis",
            instruction="You're a specialist in code execution and computational tasks. Write clean, efficient code.",
            code_executor=BuiltInCodeExecutor()
        )
        
        self.root_agent = LlmAgent(
            name="RootAgent",
            model="gemini-2.5-flash",
            description="Coordinates other agents and makes high-level decisions",
            instruction="You coordinate specialized agents to solve complex problems. Delegate appropriately.",
            tools=[
                agent_tool.AgentTool(agent=self.search_agent),
                agent_tool.AgentTool(agent=self.coding_agent)
            ]
        )
        
        self.graph = None
    
    def generate_query(self, state: OverallState) -> OverallState:
        """Generate search queries based on the input"""
        query = state.get("query", "")
        # Initialize iteration count if not set
        if "iteration_count" not in state:
            state["iteration_count"] = 0
        return state
    
    def web_research(self, state: OverallState) -> OverallState:
        """Perform web research"""
        # Increment iteration count at the start of each research cycle
        state["iteration_count"] = state.get("iteration_count", 0) + 1
        
        # Simulate research (in production, would call actual search)
        results = [
            f"Research finding {state['iteration_count']} for: {state['query']}",
            f"Research detail {state['iteration_count']} for: {state['query']}"
        ]
        state["search_results"] = state.get("search_results", []) + results
        return state
    
    def reflection(self, state: OverallState) -> OverallState:
        """Reflect on the gathered information"""
        # Evaluate quality of findings
        reflection = f"Quality assessment of iteration {state['iteration_count']}"
        state["reflections"] = state.get("reflections", []) + [reflection]
        
        # Simulate quality scoring
        state["quality_score"] = 0.8 if state["iteration_count"] >= 2 else 0.5
        return state
    
    def finalize_answer(self, state: OverallState) -> OverallState:
        """Compile final answer from research"""
        state["final_answer"] = f"Final answer based on {len(state.get('search_results', []))} findings"
        return state
    
    def continue_to_web_research(self, state: OverallState) -> str:
        """Decide whether to continue researching"""
        return "web_research"
    
    def evaluate_research(self, state: OverallState) -> str:
        """Evaluate if we have sufficient information"""
        quality_score = state.get("quality_score", 0)
        iteration_count = state.get("iteration_count", 0)
        
        # Hard limit: always stop after 3 iterations
        if iteration_count >= 3:
            return "finalize_answer"
        
        # Quality-based decision: continue if quality is below threshold
        if quality_score < 0.75:
            return "web_research"
        else:
            return "finalize_answer"
    
    def build_graph(self):
        """Build the reasoning graph with nodes and edges"""
        # Create graph with state management
        builder = StateGraph(OverallState)
        
        # Define the nodes we will cycle between
        builder.add_node("generate_query", self.generate_query)
        builder.add_node("web_research", self.web_research)
        builder.add_node("reflection", self.reflection)
        builder.add_node("finalize_answer", self.finalize_answer)
        
        # Set the entrypoint as generate_query
        builder.add_edge(START, "generate_query")
        
        # Add conditional edge to continue with search queries
        builder.add_conditional_edges(
            "generate_query",
            self.continue_to_web_research,
            ["web_research"]
        )
        
        # Reflect on the web research
        builder.add_edge("web_research", "reflection")
        
        # Evaluate the research - either continue or finalize
        builder.add_conditional_edges(
            "reflection",
            self.evaluate_research,
            ["web_research", "finalize_answer"]
        )
        
        # Finalize and end
        builder.add_edge("finalize_answer", END)
        
        # Compile the graph with recursion limit
        # Set a higher limit to allow iterative refinement while preventing infinite loops
        self.graph = builder.compile(
            checkpointer=None,
            interrupt_before=None,
            interrupt_after=None,
            debug=False
        )
        return self.graph
    
    def visualize_graph(self):
        """Get a text representation of the graph structure"""
        if not self.graph:
            self.build_graph()
        
        structure = """
Graph Structure:
================
START → generate_query
generate_query → web_research (conditional)
web_research → reflection
reflection → [web_research OR finalize_answer] (conditional - based on quality)
finalize_answer → END

Conditional Logic:
- After generate_query: Always proceed to web_research
- After reflection: 
  * If quality_score < 0.7 AND iteration_count < 3 → web_research (loop)
  * Otherwise → finalize_answer (exit)
"""
        return structure


def create_simple_reasoning_chain():
    """Create a simple reasoning chain for demonstration"""
    reasoning_agent = LlmAgent(
        name="ReasoningAgent",
        model="gemini-2.0-flash-thinking-exp-01-21",
        description="An agent that uses advanced reasoning capabilities",
        instruction="Think through problems step by step. Show your reasoning process."
    )
    return reasoning_agent


def demonstrate_agent_delegation():
    """Demonstrate hierarchical agent delegation"""
    # Create specialist agents
    search_specialist = LlmAgent(
        model='gemini-2.5-flash',
        name='SearchSpecialist',
        description="Expert at finding information",
        instruction="Find and summarize relevant information accurately."
    )
    
    code_specialist = LlmAgent(
        model='gemini-2.5-flash',
        name='CodeSpecialist',
        description="Expert at writing and executing code",
        instruction="Write clean, efficient code to solve problems.",
        code_executor=BuiltInCodeExecutor()
    )
    
    # Create coordinator that can delegate to specialists
    coordinator = LlmAgent(
        name="Coordinator",
        model="gemini-2.5-flash",
        description="Coordinates specialist agents",
        instruction="Delegate tasks to the most appropriate specialist agent.",
        tools=[
            agent_tool.AgentTool(agent=search_specialist),
            agent_tool.AgentTool(agent=code_specialist)
        ]
    )
    
    return coordinator, search_specialist, code_specialist
