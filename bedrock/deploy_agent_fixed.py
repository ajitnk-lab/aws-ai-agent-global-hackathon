#!/usr/bin/env python3
import boto3
import json

def create_bedrock_agent_fixed():
    """Deploy Bedrock Agent with proper OpenAPI 3.0 schema"""
    
    bedrock_client = boto3.client('bedrock-agent', region_name='us-east-1')
    agent_id = "KS91Z9H2MA"
    lambda_arn = "arn:aws:lambda:us-east-1:039920874011:function:security-agent-bridge"
    
    # Proper OpenAPI 3.0 schema for Bedrock Agent
    openapi_schema = {
        "openapi": "3.0.0",
        "info": {
            "title": "Security Assessment API",
            "version": "1.0.0",
            "description": "AWS Security Assessment Tools"
        },
        "paths": {
            "/checkSecurityServices": {
                "post": {
                    "summary": "Check AWS security services configuration",
                    "operationId": "checkSecurityServices",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "region": {
                                            "type": "string",
                                            "description": "AWS region to check"
                                        }
                                    }
                                }
                            }
                        }
                    },
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
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "severity": {
                                            "type": "string",
                                            "description": "Filter by severity level"
                                        },
                                        "limit": {
                                            "type": "integer",
                                            "description": "Maximum number of findings"
                                        }
                                    }
                                }
                            }
                        }
                    },
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
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "include_recommendations": {
                                            "type": "boolean",
                                            "description": "Include recommendations"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Security posture analysis"
                        }
                    }
                }
            }
        }
    }
    
    try:
        # Delete existing action group
        action_groups = bedrock_client.list_agent_action_groups(
            agentId=agent_id,
            agentVersion='DRAFT'
        )
        
        for ag in action_groups['actionGroupSummaries']:
            bedrock_client.delete_agent_action_group(
                agentId=agent_id,
                agentVersion='DRAFT',
                actionGroupId=ag['actionGroupId']
            )
            print(f"Deleted existing action group: {ag['actionGroupId']}")
        
        # Create new action group with proper OpenAPI schema
        action_group_response = bedrock_client.create_agent_action_group(
            agentId=agent_id,
            agentVersion='DRAFT',
            actionGroupName='security-tools-fixed',
            description='AWS Security Assessment Tools with proper OpenAPI schema',
            actionGroupExecutor={
                'lambda': lambda_arn
            },
            apiSchema={
                'payload': json.dumps(openapi_schema)
            }
        )
        
        print(f"Created fixed action group: {action_group_response['agentActionGroup']['actionGroupId']}")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    if create_bedrock_agent_fixed():
        print("✅ OpenAPI 3.0 schema fixed!")
    else:
        print("❌ Schema fix failed!")
