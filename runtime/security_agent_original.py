"""
AgentCore Runtime application for AWS Security Assessment
"""
import os
import json
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from bedrock_agentcore.memory import MemoryClient
from strands import Agent, tool
from strands.hooks import AgentInitializedEvent, HookProvider, MessageAddedEvent
from security_tools import SecurityAssessmentTools

# Initialize AgentCore app
app = BedrockAgentCoreApp()

# Memory and security tools setup
MEMORY_ID = os.getenv('BEDROCK_AGENTCORE_MEMORY_ID')
REGION = os.getenv('AWS_REGION', 'us-east-1')

memory_client = MemoryClient(region_name=REGION) if MEMORY_ID else None
security_tools = SecurityAssessmentTools(region=REGION)

class SecurityMemoryHook(HookProvider):
    """Memory hook for security context persistence"""
    
    def on_agent_initialized(self, event):
        if not MEMORY_ID or not memory_client:
            return
            
        # Load previous security context
        turns = memory_client.get_last_k_turns(
            memory_id=MEMORY_ID,
            actor_id="security_analyst",
            session_id=event.agent.state.get("session_id") or "default",
            k=5
        )
        
        if turns:
            context = "\n".join([
                f"{m['role']}: {m['content']['text']}"
                for t in turns for m in t
            ])
            event.agent.system_prompt += f"\n\nPrevious Security Context:\n{context}"
    
    def on_message_added(self, event):
        if not MEMORY_ID or not memory_client:
            return
            
        msg = event.agent.messages[-1]
        memory_client.create_event(
            memory_id=MEMORY_ID,
            actor_id="security_analyst",
            session_id=event.agent.state.get("session_id") or "default",
            messages=[(str(msg["content"]), msg["role"])]
        )
    
    def register_hooks(self, registry):
        registry.add_callback(AgentInitializedEvent, self.on_agent_initialized)
        registry.add_callback(MessageAddedEvent, self.on_message_added)

# Security assessment tools
@tool
def check_security_services() -> str:
    """Monitor AWS security services operational status across your infrastructure"""
    try:
        result = security_tools.check_security_services()
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error checking security services: {str(e)}"

@tool
def get_security_findings(severity_filter: str = None, limit: int = 50, region: str = None, service_filter: str = None, resource_type: str = None, compliance_status: str = None) -> str:
    """Retrieve security findings from AWS services
    
    Parameters:
    - severity_filter: LOW, MEDIUM, HIGH, CRITICAL
    - limit: Number of results (default 50)
    - region: AWS region (us-east-1, us-west-2, etc.)
    - service_filter: SecurityHub, GuardDuty, Inspector
    - resource_type: EC2, S3, IAM, etc.
    - compliance_status: PASSED, FAILED, WARNING, NOT_AVAILABLE
    """
    try:
        result = security_tools.get_security_findings(
            severity_filter=severity_filter,
            limit=limit,
            region=region,
            service_filter=service_filter,
            resource_type=resource_type,
            compliance_status=compliance_status
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error getting security findings: {str(e)}"

@tool
def analyze_security_posture() -> str:
    """Comprehensive security posture analysis against AWS Well-Architected Framework"""
    try:
        result = security_tools.analyze_security_posture()
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error analyzing security posture: {str(e)}"

@tool
def explore_aws_resources(service_filter: str = None) -> str:
    """Discover AWS resources for security assessment (services: ec2, s3, rds, lambda, iam)"""
    try:
        result = security_tools.explore_aws_resources(service_filter)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error exploring AWS resources: {str(e)}"

@tool
def get_resource_compliance_status(resource_type: str = None) -> str:
    """Check compliance status of AWS resources against security standards"""
    try:
        result = security_tools.get_resource_compliance_status(resource_type)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error checking compliance status: {str(e)}"

# Create security assessment agent
agent = Agent(
    model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    system_prompt="""You are an AWS Security Assessment Agent specializing in the Well-Architected Framework Security Pillar.

Your capabilities include:
- Monitoring AWS security services operational status
- Retrieving and analyzing security findings
- Performing comprehensive security posture assessments
- Discovering and inventorying AWS resources
- Checking compliance against security standards

Always provide actionable recommendations based on AWS Well-Architected best practices.
Focus on operational security monitoring and cost-effective security improvements.""",
    tools=[
        check_security_services,
        get_security_findings,
        analyze_security_posture,
        explore_aws_resources,
        get_resource_compliance_status
    ],
    hooks=[SecurityMemoryHook()] if MEMORY_ID else [],
    state={"session_id": "default"}
)

@app.entrypoint
def invoke(payload, context):
    """Main entry point for security assessment requests"""
    # Set session ID for memory isolation
    if hasattr(context, 'session_id'):
        agent.state.set("session_id", context.session_id)
    
    # Process security assessment request
    prompt = payload.get("prompt", "Hello! I'm ready to help with AWS security assessments.")
    
    try:
        response = agent(prompt)
        return {
            "response": response.message['content'][0]['text'],
            "session_id": agent.state.get("session_id"),
            "tools_used": [tool.name for tool in response.tool_calls] if hasattr(response, 'tool_calls') else []
        }
    except Exception as e:
        return {
            "error": f"Security assessment error: {str(e)}",
            "session_id": agent.state.get("session_id")
        }

if __name__ == "__main__":
    app.run()
