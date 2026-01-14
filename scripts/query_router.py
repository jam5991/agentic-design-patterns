"""
Resource-Aware Query Routing

This module demonstrates resource-aware agentic patterns:
- Cost optimization through intelligent model selection
- Query complexity analysis
- Router agent pattern for dispatching requests
"""

from google.adk.agents import Agent, LlmAgent
from google.genai import types
import os


class QueryComplexityAnalyzer:
    """Analyzes query complexity to determine appropriate model selection."""
    
    def __init__(self, word_threshold: int = 20):
        """
        Initialize the analyzer.
        
        Args:
            word_threshold: Number of words to distinguish simple from complex queries
        """
        self.word_threshold = word_threshold
    
    def analyze(self, query: str) -> dict:
        """
        Analyze query complexity.
        
        Returns:
            dict with 'complexity' ('simple' or 'complex'), 'word_count', and 'recommended_model'
        """
        word_count = len(query.split())
        
        if word_count < self.word_threshold:
            return {
                'complexity': 'simple',
                'word_count': word_count,
                'recommended_model': 'gemini-2.0-flash-exp'
            }
        else:
            return {
                'complexity': 'complex',
                'word_count': word_count,
                'recommended_model': 'gemini-2.0-flash-thinking-exp-01-21'
            }


def create_flash_agent() -> LlmAgent:
    """
    Create an agent using the cost-effective Gemini Flash model.
    
    Returns:
        LlmAgent configured with Flash model
    """
    return LlmAgent(
        name="FlashAgent",
        model="gemini-2.0-flash-exp",
        description="A fast and efficient agent for simple queries.",
        instruction="You are a quick assistant for straightforward questions. Provide concise, accurate answers."
    )


def create_thinking_agent() -> LlmAgent:
    """
    Create an agent using the more capable Gemini Thinking model.
    
    Returns:
        LlmAgent configured with Thinking model
    """
    return LlmAgent(
        name="ThinkingAgent",
        model="gemini-2.0-flash-thinking-exp-01-21",
        description="A highly capable agent for complex queries requiring deep reasoning.",
        instruction="You are an expert assistant for complex problem-solving. Think through problems step-by-step and provide thorough, well-reasoned answers."
    )


class QueryRouter:
    """Routes queries to the appropriate agent based on complexity."""
    
    def __init__(self):
        """Initialize the router with agents and analyzer."""
        self.flash_agent = create_flash_agent()
        self.thinking_agent = create_thinking_agent()
        self.analyzer = QueryComplexityAnalyzer()
    
    def route(self, query: str) -> tuple[LlmAgent, dict]:
        """
        Route a query to the appropriate agent.
        
        Args:
            query: The user query to route
            
        Returns:
            Tuple of (selected_agent, analysis_result)
        """
        analysis = self.analyzer.analyze(query)
        
        if analysis['complexity'] == 'simple':
            print(f"🚀 Routing to Flash Agent (simple query, {analysis['word_count']} words)")
            return self.flash_agent, analysis
        else:
            print(f"🎯 Routing to Thinking Agent (complex query, {analysis['word_count']} words)")
            return self.thinking_agent, analysis
    
    async def process_query(self, query: str) -> dict:
        """
        Process a query end-to-end: analyze, route, and execute.
        
        Args:
            query: The user query to process
            
        Returns:
            Dictionary with query, analysis, agent_used, and response
        """
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
        from google.genai.types import Content, Part
        
        agent, analysis = self.route(query)
        
        # Setup session service and runner
        session_service = InMemorySessionService()
        app_name = "resource_aware_router"
        user_id = "demo_user"
        session_id = "demo_session"
        
        # Create session
        await session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id
        )
        
        # Create runner
        runner = Runner(
            agent=agent,
            app_name=app_name,
            session_service=session_service
        )
        
        # Execute the query
        user_message = Content(parts=[Part(text=query)])
        response_text = ""
        
        for event in runner.run(user_id=user_id, session_id=session_id, new_message=user_message):
            if event.is_final_response():
                response_text = event.content.parts[0].text
                break
        
        return {
            'query': query,
            'analysis': analysis,
            'agent_used': agent.name,
            'response': response_text
        }



# Cost estimation (illustrative - actual costs may vary)
COST_PER_1K_TOKENS = {
    'gemini-2.0-flash-exp': 0.0001,  # Example: very low cost
    'gemini-2.0-flash-thinking-exp-01-21': 0.0005,  # Example: higher cost for reasoning
}


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """
    Estimate the cost of using a particular model.
    
    Args:
        model: Model name
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        
    Returns:
        Estimated cost in dollars
    """
    rate = COST_PER_1K_TOKENS.get(model, 0.0001)
    total_tokens = input_tokens + output_tokens
    return (total_tokens / 1000) * rate


if __name__ == "__main__":
    # Example usage
    router = QueryRouter()
    
    # Test queries
    simple_query = "What is the capital of France?"
    complex_query = "Explain the implications of quantum entanglement for secure communication systems, including the technical challenges and potential solutions for implementing quantum key distribution at scale."
    
    print("Simple Query Analysis:")
    agent, analysis = router.route(simple_query)
    print(f"  Query: {simple_query}")
    print(f"  Analysis: {analysis}")
    print()
    
    print("Complex Query Analysis:")
    agent, analysis = router.route(complex_query)
    print(f"  Query: {complex_query[:80]}...")
    print(f"  Analysis: {analysis}")
