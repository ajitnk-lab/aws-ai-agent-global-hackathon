"""
Deploy Bedrock Agent for AgentCore Security Assessment
"""
import boto3
import json
import uuid
import os

def create_bedrock_agent():
    """Create Bedrock Agent that calls AgentCore Gateway"""
    
    region = os.getenv('AWS_REGION', 'us-east-1')
    lambda_arn = os.getenv('LAMBDA_BRIDGE_ARN')
    
    if not lambda_arn:
        print("❌ Error: LAMBDA_BRIDGE_ARN environment variable required")
        print("   Deploy the Lambda bridge first")
        return None
    
    bedrock_agent = boto3.client('bedrock-agent', region_name=region)
    iam = boto3.client('iam', region_name=region)
    
    # Create IAM role for Bedrock Agent
    print("1. Creating IAM role for Bedrock Agent...")
    
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "bedrock.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    role_name = f"BedrockSecurityAgent-{uuid.uuid4().hex[:8]}"
    
    try:
        role_response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="IAM role for Bedrock Security Assessment Agent"
        )
        
        # Attach necessary policies
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/AmazonBedrockFullAccess'
        )
        
        role_arn = role_response['Role']['Arn']
        print(f"✅ IAM role created: {role_arn}")
        
    except iam.exceptions.EntityAlreadyExistsException:
        role_arn = f"arn:aws:iam::{boto3.client('sts').get_caller_identity()['Account']}:role/{role_name}"
        print(f"✅ Using existing IAM role: {role_arn}")
    
    # Create Bedrock Agent
    print("2. Creating Bedrock Agent...")
    
    agent_name = f"SecurityAssessmentAgent-{uuid.uuid4().hex[:8]}"
    
    agent_response = bedrock_agent.create_agent(
        agentName=agent_name,
        foundationModel='anthropic.claude-3-sonnet-20240229-v1:0',
        instruction="""You are an AWS Security Assessment Agent specializing in the Well-Architected Framework Security Pillar.

Your mission is to help organizations assess and improve their AWS security posture through:

1. **Security Service Monitoring**: Check the operational status of AWS security services
2. **Finding Analysis**: Retrieve and analyze security findings from multiple AWS services  
3. **Posture Assessment**: Perform comprehensive security assessments against Well-Architected best practices
4. **Resource Discovery**: Inventory AWS resources for security evaluation
5. **Compliance Checking**: Verify resource compliance against security standards

Always provide actionable recommendations based on AWS Well-Architected Framework principles.
Focus on operational security improvements and cost-effective security enhancements.

When users ask about security assessments, use the available tools to gather current data and provide specific, actionable guidance.""",
        agentResourceRoleArn=role_arn,
        description="AWS Security Assessment Agent with Well-Architected Framework expertise"
    )
    
    agent_id = agent_response['agent']['agentId']
    print(f"✅ Bedrock Agent created: {agent_id}")
    
    # Create Action Group
    print("3. Creating Action Group for AgentCore tools...")
    
    # OpenAPI schema for AgentCore security tools
    openapi_schema = {
        "openapi": "3.0.0",
        "info": {
            "title": "AgentCore Security Assessment API",
            "version": "1.0.0",
            "description": "AWS Security Assessment tools via AgentCore Gateway"
        },
        "paths": {
            "/check-security-services": {
                "post": {
                    "operationId": "checkSecurityServices",
                    "summary": "Monitor AWS security services operational status",
                    "description": "Check the status of GuardDuty, Security Hub, Inspector, and IAM Access Analyzer",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {}
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Security services status",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/get-security-findings": {
                "post": {
                    "operationId": "getSecurityFindings",
                    "summary": "Retrieve security findings from AWS services",
                    "description": "Get security findings from Security Hub, GuardDuty, and Inspector",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "severity_filter": {
                                            "type": "string",
                                            "enum": ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
                                            "description": "Filter findings by severity level"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Security findings",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/analyze-security-posture": {
                "post": {
                    "operationId": "analyzeSecurityPosture",
                    "summary": "Comprehensive security posture analysis",
                    "description": "Analyze security posture against AWS Well-Architected Framework",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {}
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Security posture analysis",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/explore-aws-resources": {
                "post": {
                    "operationId": "exploreAwsResources",
                    "summary": "Discover AWS resources for security assessment",
                    "description": "Inventory AWS resources across services for security evaluation",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "service_filter": {
                                            "type": "string",
                                            "enum": ["ec2", "s3", "rds", "lambda", "iam"],
                                            "description": "Filter resources by AWS service"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "AWS resources inventory",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/get-compliance-status": {
                "post": {
                    "operationId": "getComplianceStatus",
                    "summary": "Check resource compliance against security standards",
                    "description": "Verify AWS resource compliance with security standards",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "resource_type": {
                                            "type": "string",
                                            "description": "Filter by specific resource type"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Compliance status",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    action_group_response = bedrock_agent.create_agent_action_group(
        agentId=agent_id,
        agentVersion='DRAFT',
        actionGroupName='SecurityAssessmentTools',
        description='AgentCore security assessment tools',
        actionGroupExecutor={
            'lambda': lambda_arn
        },
        apiSchema={
            'payload': json.dumps(openapi_schema)
        }
    )
    
    print(f"✅ Action Group created: {action_group_response['agentActionGroup']['actionGroupId']}")
    
    # Prepare the agent
    print("4. Preparing Bedrock Agent...")
    
    prepare_response = bedrock_agent.prepare_agent(
        agentId=agent_id
    )
    
    print(f"✅ Agent prepared: {prepare_response['agentStatus']}")
    
    # Save configuration
    config = {
        "agent_id": agent_id,
        "agent_name": agent_name,
        "role_arn": role_arn,
        "lambda_arn": lambda_arn,
        "action_group_id": action_group_response['agentActionGroup']['actionGroupId']
    }
    
    with open('bedrock_agent_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Bedrock Agent deployment complete!")
    print(f"   Agent ID: {agent_id}")
    print(f"   Agent Name: {agent_name}")
    print(f"   Configuration saved to: bedrock_agent_config.json")
    
    return config

if __name__ == "__main__":
    config = create_bedrock_agent()
    if config:
        print(f"\n🎯 Agent ID: {config['agent_id']}")
        print("Your Bedrock Agent is ready to perform security assessments!")
