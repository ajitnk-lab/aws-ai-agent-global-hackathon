"""
Minimal debug version of security_agent.py
"""
import os
import json
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
from security_tools import SecurityAssessmentTools

app = BedrockAgentCoreApp()
REGION = os.getenv('AWS_REGION', 'us-east-1')
security_tools = SecurityAssessmentTools(region=REGION)

@tool
def debug_test() -> str:
    """Simple debug test"""
    return "Debug test successful"

@tool
def get_security_findings_debug(limit: int = 5) -> str:
    """Debug version of get_security_findings"""
    try:
        result = security_tools.get_security_findings(limit=limit)
        return f"SUCCESS: Found {result.get('total_findings', 0)} findings"
    except Exception as e:
        return f"ERROR: {str(e)}"

agent = Agent(
    name="security_analyst",
    tools=[debug_test, get_security_findings_debug]
)

app.add_agent(agent)
