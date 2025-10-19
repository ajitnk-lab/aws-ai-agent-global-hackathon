"""
Setup AgentCore Gateway with OAuth integration for security tools
"""
from bedrock_agentcore.gateway import GatewayClient
import json
import uuid
import os

def create_security_gateway():
    """Create Gateway with OAuth for security assessment tools"""
    
    region = os.getenv('AWS_REGION', 'us-east-1')
    runtime_arn = os.getenv('AGENTCORE_RUNTIME_ARN')
    
    if not runtime_arn:
        print("❌ Error: AGENTCORE_RUNTIME_ARN environment variable required")
        print("   Deploy the runtime first and set the ARN")
        return None
    
    client = GatewayClient(region_name=region)
    gateway_name = f"SecurityAssessment_{uuid.uuid4().hex[:8]}"
    
    print("Creating AgentCore Gateway with OAuth...")
    
    # Create Cognito OAuth authorizer
    print("1. Creating OAuth authorization server...")
    cognito = client.create_oauth_authorizer_with_cognito(gateway_name)
    print("✅ OAuth authorization server created")
    
    # Define security tools schema for Gateway
    security_tools_schema = {
        "runtime_arn": runtime_arn,
        "tools": [
            {
                "name": "check_security_services",
                "description": "Monitor AWS security services operational status across your infrastructure",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_security_findings", 
                "description": "Retrieve security findings from AWS services",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "severity_filter": {
                            "type": "string",
                            "enum": ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
                            "description": "Filter findings by severity level"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "analyze_security_posture",
                "description": "Comprehensive security posture analysis against AWS Well-Architected Framework",
                "inputSchema": {
                    "type": "object", 
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "explore_aws_resources",
                "description": "Discover AWS resources for security assessment",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "service_filter": {
                            "type": "string",
                            "enum": ["ec2", "s3", "rds", "lambda", "iam"],
                            "description": "Filter resources by AWS service"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "get_resource_compliance_status",
                "description": "Check compliance status of AWS resources against security standards",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "resource_type": {
                            "type": "string",
                            "description": "Filter by specific resource type"
                        }
                    },
                    "required": []
                }
            }
        ]
    }
    
    # Create Gateway
    print("2. Creating Gateway...")
    gateway = client.setup_gateway(
        gateway_name=gateway_name,
        target_source=json.dumps(security_tools_schema),
        execution_role_arn=None,  # Auto-create IAM role
        authorizer_config=cognito['authorizer_config'],
        target_type='runtime',
        enable_semantic_search=True,
        description="AWS Security Assessment Gateway with Well-Architected Framework tools"
    )
    print("✅ Gateway created")
    
    # Save configuration
    config = {
        "gateway_url": gateway.get_mcp_url(),
        "gateway_id": gateway.gateway_id if hasattr(gateway, 'gateway_id') else 'unknown',
        "cognito_client_id": cognito['client_info']['client_id'],
        "cognito_client_secret": cognito['client_info']['client_secret'],
        "cognito_token_endpoint": cognito['client_info']['token_endpoint'],
        "cognito_scope": cognito['client_info']['scope'],
        "runtime_arn": runtime_arn
    }
    
    with open('gateway_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Gateway setup complete!")
    print(f"   Gateway URL: {config['gateway_url']}")
    print(f"   OAuth Client ID: {config['cognito_client_id']}")
    print(f"   Configuration saved to: gateway_config.json")
    
    return config

if __name__ == "__main__":
    config = create_security_gateway()
    if config:
        print(f"\n🎯 Gateway URL: {config['gateway_url']}")
        print("Use this configuration for Bedrock Agent integration.")
