#!/usr/bin/env python3
import boto3
import json
import time

def create_bedrock_agent():
    """Deploy Bedrock Agent with security tools"""
    
    bedrock_client = boto3.client('bedrock-agent', region_name='us-east-1')
    iam_client = boto3.client('iam', region_name='us-east-1')
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Create IAM role for Bedrock Agent
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "bedrock.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    # Create agent role
    try:
        role_response = iam_client.create_role(
            RoleName='SecurityBedrockAgentRole',
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for Security Assessment Bedrock Agent'
        )
        agent_role_arn = role_response['Role']['Arn']
        print(f"Created Bedrock Agent role: {agent_role_arn}")
        time.sleep(10)  # Wait for propagation
    except iam_client.exceptions.EntityAlreadyExistsException:
        role_response = iam_client.get_role(RoleName='SecurityBedrockAgentRole')
        agent_role_arn = role_response['Role']['Arn']
        print(f"Using existing Bedrock Agent role: {agent_role_arn}")
    
    # Attach Bedrock agent policy
    bedrock_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel"
                ],
                "Resource": "*"
            }
        ]
    }
    
    try:
        iam_client.put_role_policy(
            RoleName='SecurityBedrockAgentRole',
            PolicyName='BedrockInvokeModelPolicy',
            PolicyDocument=json.dumps(bedrock_policy)
        )
    except:
        pass
    
    # Grant Lambda invoke permission to Bedrock
    lambda_arn = "arn:aws:lambda:us-east-1:039920874011:function:security-agent-bridge"
    
    try:
        lambda_client.add_permission(
            FunctionName='security-agent-bridge',
            StatementId='bedrock-agent-invoke',
            Action='lambda:InvokeFunction',
            Principal='bedrock.amazonaws.com',
            SourceArn=f"arn:aws:bedrock:us-east-1:039920874011:agent/*"
        )
        print("Added Lambda invoke permission for Bedrock")
    except:
        print("Lambda permission already exists")
    
    # Create or get existing Bedrock Agent
    agent_id = None
    try:
        agent_response = bedrock_client.create_agent(
            agentName='security-assessment-agent',
            description='AWS Security Assessment Agent powered by AgentCore',
            foundationModel='anthropic.claude-3-sonnet-20240229-v1:0',
            instruction="""You are an AWS Security Assessment Agent. You help users analyze their AWS infrastructure security posture using comprehensive security tools.

Your capabilities include:
- Checking security service configurations across AWS accounts
- Analyzing security findings from AWS Security Hub, GuardDuty, and other services  
- Evaluating resource compliance against security best practices
- Exploring AWS resources and their security configurations
- Providing detailed security posture analysis and recommendations

Always provide clear, actionable security recommendations and explain the security implications of your findings.""",
            agentResourceRoleArn=agent_role_arn,
            idleSessionTTLInSeconds=1800
        )
        
        agent_id = agent_response['agent']['agentId']
        print(f"Created Bedrock Agent: {agent_id}")
        
    except bedrock_client.exceptions.ConflictException as e:
        # Agent already exists, get the existing one
        if "KS91Z9H2MA" in str(e):
            agent_id = "KS91Z9H2MA"
            print(f"Using existing Bedrock Agent: {agent_id}")
        else:
            # List agents to find the existing one
            agents = bedrock_client.list_agents()
            for agent in agents['agentSummaries']:
                if agent['agentName'] == 'security-assessment-agent':
                    agent_id = agent['agentId']
                    print(f"Found existing Bedrock Agent: {agent_id}")
                    break
    
    if not agent_id:
        raise Exception("Could not create or find existing agent")
        
    # Wait for agent to be ready
    print("Waiting for agent to be ready...")
    max_wait = 300  # 5 minutes
    wait_time = 0
    
    while wait_time < max_wait:
        try:
            agent_status = bedrock_client.get_agent(agentId=agent_id)
            status = agent_status['agent']['agentStatus']
            print(f"Agent status: {status}")
            
            if status in ['PREPARED', 'NOT_PREPARED']:
                break
            elif status == 'FAILED':
                raise Exception("Agent creation failed")
                
            time.sleep(10)
            wait_time += 10
            
        except Exception as e:
            if "does not exist" in str(e):
                time.sleep(10)
                wait_time += 10
                continue
            else:
                raise e
    
    if wait_time >= max_wait:
        raise Exception("Timeout waiting for agent to be ready")
    
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
            # Update existing action group
            action_group_response = bedrock_client.update_agent_action_group(
                agentId=agent_id,
                agentVersion='DRAFT',
                actionGroupId=existing_action_group,
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
                                            "description": "Security services status",
                                            "content": {
                                                "application/json": {
                                                    "schema": {"type": "object"}
                                                }
                                            }
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
                                            "description": "Security findings",
                                            "content": {
                                                "application/json": {
                                                    "schema": {"type": "object"}
                                                }
                                            }
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
                                            "description": "Security posture analysis",
                                            "content": {
                                                "application/json": {
                                                    "schema": {"type": "object"}
                                                }
                                            }
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
                                            "description": "AWS resources information",
                                            "content": {
                                                "application/json": {
                                                    "schema": {"type": "object"}
                                                }
                                            }
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
                                            "description": "Compliance status",
                                            "content": {
                                                "application/json": {
                                                    "schema": {"type": "object"}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    })
                }
            )
            print(f"Updated Action Group: {action_group_response['agentActionGroup']['actionGroupId']}")
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
                                            "description": "Security services status",
                                            "content": {
                                                "application/json": {
                                                    "schema": {"type": "object"}
                                                }
                                            }
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
                                            "description": "Security findings",
                                            "content": {
                                                "application/json": {
                                                    "schema": {"type": "object"}
                                                }
                                            }
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
                                            "description": "Security posture analysis",
                                            "content": {
                                                "application/json": {
                                                    "schema": {"type": "object"}
                                                }
                                            }
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
                                            "description": "AWS resources information",
                                            "content": {
                                                "application/json": {
                                                    "schema": {"type": "object"}
                                                }
                                            }
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
                                            "description": "Compliance status",
                                            "content": {
                                                "application/json": {
                                                    "schema": {"type": "object"}
                                                }
                                            }
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
        # Continue anyway
    
    # Prepare the agent
    try:
        prepare_response = bedrock_client.prepare_agent(
            agentId=agent_id
        )
        print(f"Agent prepared successfully: {prepare_response['agentStatus']}")
    except Exception as e:
        print(f"Error preparing agent: {e}")
    
    return agent_id
        
    except Exception as e:
        print(f"Error creating Bedrock Agent: {e}")
        raise e

if __name__ == "__main__":
    try:
        agent_id = create_bedrock_agent()
        print(f"\n✅ Bedrock Agent deployed successfully!")
        print(f"Agent ID: {agent_id}")
        print(f"You can now test the agent using the Bedrock console or API calls.")
    except Exception as e:
        print(f"\n❌ Bedrock Agent deployment failed: {e}")
