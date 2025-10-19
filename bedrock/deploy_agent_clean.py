#!/usr/bin/env python3
import boto3
import json
import time

def create_bedrock_agent():
    """Deploy Bedrock Agent with security tools"""
    
    bedrock_client = boto3.client('bedrock-agent', region_name='us-east-1')
    iam_client = boto3.client('iam', region_name='us-east-1')
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Use existing agent
    agent_id = "KS91Z9H2MA"
    print(f"Using existing Bedrock Agent: {agent_id}")
    
    # Lambda ARN
    lambda_arn = "arn:aws:lambda:us-east-1:039920874011:function:security-agent-bridge"
    
    # Check if action group already exists
    try:
        action_groups = bedrock_client.list_agent_action_groups(
            agentId=agent_id,
            agentVersion='DRAFT'
        )
        
        existing_action_group = None
        for ag in action_groups['actionGroupSummaries']:
            if ag['actionGroupName'] == 'security-tools':
                existing_action_group = ag['actionGroupId']
                print(f"Found existing action group: {existing_action_group}")
                break
        
        if existing_action_group:
            print("Action group already exists, skipping creation")
        else:
            # Create new action group
            action_group_response = bedrock_client.create_agent_action_group(
                agentId=agent_id,
                agentVersion='DRAFT',
                actionGroupName='security-tools',
                description='AWS Security Assessment Tools',
                actionGroupExecutor={
                    'lambda': lambda_arn
                },
                apiSchema={
                    'payload': json.dumps({
                        "openapi": "3.0.0",
                        "info": {
                            "title": "AWS Security Assessment API",
                            "version": "1.0.0",
                            "description": "Comprehensive AWS security assessment tools"
                        },
                        "paths": {
                            "/checkSecurityServices": {
                                "post": {
                                    "summary": "Check AWS security services configuration",
                                    "operationId": "checkSecurityServices",
                                    "parameters": [
                                        {
                                            "name": "region",
                                            "in": "query",
                                            "schema": {"type": "string"},
                                            "description": "AWS region to check"
                                        }
                                    ],
                                    "responses": {
                                        "200": {
                                            "description": "Security services status"
                                        }
                                    }
                                }
                            },
                            "/getSecurityFindings": {
                                "post": {
                                    "summary": "Get security findings from AWS Security Hub",
                                    "operationId": "getSecurityFindings",
                                    "parameters": [
                                        {
                                            "name": "severity",
                                            "in": "query", 
                                            "schema": {"type": "string"},
                                            "description": "Filter by severity (CRITICAL, HIGH, MEDIUM, LOW)"
                                        },
                                        {
                                            "name": "limit",
                                            "in": "query",
                                            "schema": {"type": "integer"},
                                            "description": "Maximum number of findings to return"
                                        }
                                    ],
                                    "responses": {
                                        "200": {
                                            "description": "Security findings"
                                        }
                                    }
                                }
                            },
                            "/analyzeSecurityPosture": {
                                "post": {
                                    "summary": "Analyze overall security posture",
                                    "operationId": "analyzeSecurityPosture",
                                    "parameters": [
                                        {
                                            "name": "include_recommendations",
                                            "in": "query",
                                            "schema": {"type": "boolean"},
                                            "description": "Include security recommendations"
                                        }
                                    ],
                                    "responses": {
                                        "200": {
                                            "description": "Security posture analysis"
                                        }
                                    }
                                }
                            },
                            "/exploreAwsResources": {
                                "post": {
                                    "summary": "Explore AWS resources and configurations",
                                    "operationId": "exploreAwsResources",
                                    "parameters": [
                                        {
                                            "name": "service",
                                            "in": "query",
                                            "schema": {"type": "string"},
                                            "description": "AWS service to explore (ec2, s3, iam, etc.)"
                                        },
                                        {
                                            "name": "region",
                                            "in": "query",
                                            "schema": {"type": "string"},
                                            "description": "AWS region to explore"
                                        }
                                    ],
                                    "responses": {
                                        "200": {
                                            "description": "AWS resources information"
                                        }
                                    }
                                }
                            },
                            "/getComplianceStatus": {
                                "post": {
                                    "summary": "Get resource compliance status",
                                    "operationId": "getComplianceStatus",
                                    "parameters": [
                                        {
                                            "name": "resource_type",
                                            "in": "query",
                                            "schema": {"type": "string"},
                                            "description": "Type of AWS resource to check"
                                        },
                                        {
                                            "name": "compliance_type",
                                            "in": "query",
                                            "schema": {"type": "string"},
                                            "description": "Compliance framework (CIS, SOC2, PCI-DSS)"
                                        }
                                    ],
                                    "responses": {
                                        "200": {
                                            "description": "Compliance status"
                                        }
                                    }
                                }
                            }
                        }
                    })
                }
            )
            print(f"Created Action Group: {action_group_response['agentActionGroup']['actionGroupId']}")
        
    except Exception as e:
        print(f"Error with action group: {e}")
        return None
    
    # Prepare the agent
    try:
        prepare_response = bedrock_client.prepare_agent(
            agentId=agent_id
        )
        print(f"Agent prepared successfully: {prepare_response['agentStatus']}")
    except Exception as e:
        print(f"Error preparing agent: {e}")
    
    return agent_id

if __name__ == "__main__":
    try:
        agent_id = create_bedrock_agent()
        if agent_id:
            print(f"\n✅ Bedrock Agent configured successfully!")
            print(f"Agent ID: {agent_id}")
            print(f"You can now test the agent using the Bedrock console or API calls.")
        else:
            print(f"\n❌ Bedrock Agent configuration failed!")
    except Exception as e:
        print(f"\n❌ Bedrock Agent deployment failed: {e}")
