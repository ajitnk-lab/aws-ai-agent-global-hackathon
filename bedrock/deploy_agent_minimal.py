#!/usr/bin/env python3
import boto3
import json

def create_bedrock_agent():
    """Deploy Bedrock Agent with minimal security tools"""
    
    bedrock_client = boto3.client('bedrock-agent', region_name='us-east-1')
    
    # Use existing agent
    agent_id = "KS91Z9H2MA"
    print(f"Using existing Bedrock Agent: {agent_id}")
    
    # Lambda ARN
    lambda_arn = "arn:aws:lambda:us-east-1:039920874011:function:security-agent-bridge"
    
    # Minimal valid OpenAPI schema
    openapi_schema = {
        "openapi": "3.0.0",
        "info": {
            "title": "Security Tools",
            "version": "1.0.0"
        },
        "paths": {
            "/security": {
                "post": {
                    "operationId": "checkSecurity",
                    "summary": "Check security status",
                    "responses": {
                        "200": {
                            "description": "Success"
                        }
                    }
                }
            }
        }
    }
    
    try:
        # Create action group
        action_group_response = bedrock_client.create_agent_action_group(
            agentId=agent_id,
            agentVersion='DRAFT',
            actionGroupName='security-tools',
            description='AWS Security Assessment Tools',
            actionGroupExecutor={
                'lambda': lambda_arn
            },
            apiSchema={
                'payload': json.dumps(openapi_schema)
            }
        )
        print(f"Created Action Group: {action_group_response['agentActionGroup']['actionGroupId']}")
        
        # Prepare the agent
        prepare_response = bedrock_client.prepare_agent(
            agentId=agent_id
        )
        print(f"Agent prepared: {prepare_response['agentStatus']}")
        
        return agent_id
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    agent_id = create_bedrock_agent()
    if agent_id:
        print(f"\n✅ Bedrock Agent configured successfully!")
        print(f"Agent ID: {agent_id}")
    else:
        print(f"\n❌ Bedrock Agent configuration failed!")
