"""
Debug version of security_agent.py with detailed logging
"""
import os
import json
import traceback
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

print(f"DEBUG: Initialized SecurityAssessmentTools with region: {REGION}")

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
            event_type="message",
            content=msg.content
        )

# Security assessment tools
@tool
def check_security_services() -> str:
    """Monitor AWS security services operational status across your infrastructure"""
    try:
        print("DEBUG: check_security_services called")
        result = security_tools.check_security_services()
        print(f"DEBUG: check_security_services result: {result}")
        return json.dumps(result, indent=2)
    except Exception as e:
        print(f"DEBUG: check_security_services error: {e}")
        traceback.print_exc()
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
        print(f"DEBUG: get_security_findings called with:")
        print(f"  severity_filter: {severity_filter}")
        print(f"  limit: {limit}")
        print(f"  region: {region}")
        print(f"  service_filter: {service_filter}")
        print(f"  resource_type: {resource_type}")
        print(f"  compliance_status: {compliance_status}")
        
        result = security_tools.get_security_findings(
            severity_filter=severity_filter,
            limit=limit,
            region=region,
            service_filter=service_filter,
            resource_type=resource_type,
            compliance_status=compliance_status
        )
        
        print(f"DEBUG: get_security_findings result type: {type(result)}")
        print(f"DEBUG: get_security_findings result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        if isinstance(result, dict):
            print(f"DEBUG: Total findings: {result.get('total_findings', 'Unknown')}")
            print(f"DEBUG: Status: {result.get('status', 'Unknown')}")
            findings = result.get('findings', [])
            print(f"DEBUG: Findings list length: {len(findings)}")
            if findings:
                print(f"DEBUG: First finding: {findings[0]}")
        
        json_result = json.dumps(result, indent=2)
        print(f"DEBUG: JSON result length: {len(json_result)}")
        return json_result
        
    except Exception as e:
        print(f"DEBUG: get_security_findings error: {e}")
        traceback.print_exc()
        return f"Error getting security findings: {str(e)}"

@tool
def analyze_security_posture() -> str:
    """Comprehensive security posture analysis against AWS Well-Architected Framework"""
    try:
        print("DEBUG: analyze_security_posture called")
        result = security_tools.analyze_security_posture()
        print(f"DEBUG: analyze_security_posture result: {result}")
        return json.dumps(result, indent=2)
    except Exception as e:
        print(f"DEBUG: analyze_security_posture error: {e}")
        traceback.print_exc()
        return f"Error analyzing security posture: {str(e)}"

@tool
def explore_aws_resources(service_filter: str = None) -> str:
    """Discover AWS resources for security assessment (services: ec2, s3, rds, lambda, iam)"""
    try:
        print(f"DEBUG: explore_aws_resources called with service_filter: {service_filter}")
        result = security_tools.explore_aws_resources(service_filter=service_filter)
        print(f"DEBUG: explore_aws_resources result: {result}")
        return json.dumps(result, indent=2)
    except Exception as e:
        print(f"DEBUG: explore_aws_resources error: {e}")
        traceback.print_exc()
        return f"Error exploring AWS resources: {str(e)}"

@tool
def get_resource_compliance_status(resource_type: str = None) -> str:
    """Check compliance status of AWS resources against security standards"""
    try:
        print(f"DEBUG: get_resource_compliance_status called with resource_type: {resource_type}")
        result = security_tools.get_resource_compliance_status(resource_type=resource_type)
        print(f"DEBUG: get_resource_compliance_status result: {result}")
        return json.dumps(result, indent=2)
    except Exception as e:
        print(f"DEBUG: get_resource_compliance_status error: {e}")
        traceback.print_exc()
        return f"Error getting compliance status: {str(e)}"

# Create agent with memory hook
agent = Agent(
    name="security_analyst",
    instructions="""You are an AWS Security Assessment Agent powered by AgentCore.
    
    Your role is to help users understand and improve their AWS security posture by:
    1. Monitoring security services (GuardDuty, Security Hub, Inspector, Access Analyzer)
    2. Analyzing security findings and vulnerabilities
    3. Providing Well-Architected Framework guidance
    4. Recommending security improvements
    
    Always provide actionable insights and prioritize critical security issues.
    Use the available tools to gather current security data and provide comprehensive assessments.
    """,
    tools=[
        check_security_services,
        get_security_findings,
        analyze_security_posture,
        explore_aws_resources,
        get_resource_compliance_status
    ],
    hooks=[SecurityMemoryHook()]
)

# Register agent with AgentCore
app.add_agent(agent)
