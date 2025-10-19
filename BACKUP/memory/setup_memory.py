"""
Setup AgentCore Memory for security context persistence
"""
from bedrock_agentcore.memory import MemoryClient
import uuid
import os

def create_security_memory():
    """Create memory resources for security assessment context"""
    
    region = os.getenv('AWS_REGION', 'us-east-1')
    client = MemoryClient(region_name=region)
    
    print("Creating AgentCore Memory for Security Assessment...")
    
    # Create memory with security-focused strategies
    memory = client.create_memory_and_wait(
        name=f"SecurityAssessment_{uuid.uuid4().hex[:8]}",
        strategies=[
            # Store security findings
            {
                "semanticMemoryStrategy": {
                    "name": "security_findings",
                    "namespaces": ["/security/findings"]
                }
            },
            # Store security preferences
            {
                "userPreferenceMemoryStrategy": {
                    "name": "security_preferences", 
                    "namespaces": ["/security/preferences"]
                }
            }
        ],
        event_expiry_days=90  # Keep security context for 90 days
    )
    
    print(f"✅ Security Memory Created: {memory['id']}")
    print(f"   Memory Type: Long-term with security-focused strategies")
    print(f"   Retention: 90 days")
    print(f"   Strategies: Security findings, preferences, compliance context")
    
    # Save memory ID to environment file
    with open('.env', 'w') as f:
        f.write(f"BEDROCK_AGENTCORE_MEMORY_ID={memory['id']}\n")
        f.write(f"AWS_REGION={region}\n")
    
    print(f"\n📝 Configuration saved to .env file")
    print(f"   Set environment: export BEDROCK_AGENTCORE_MEMORY_ID={memory['id']}")
    
    return memory

if __name__ == "__main__":
    memory = create_security_memory()
    print(f"\n🎯 Memory ID: {memory['id']}")
    print("Use this ID when deploying the runtime and gateway.")
