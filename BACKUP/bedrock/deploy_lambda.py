#!/usr/bin/env python3
import boto3
import zipfile
import os
import json
import time
from pathlib import Path

def create_lambda_package():
    """Create deployment package for Lambda function"""
    
    # Create deployment directory
    deploy_dir = Path("lambda_deploy")
    deploy_dir.mkdir(exist_ok=True)
    
    # Copy Lambda function
    with open("lambda_bridge.py", "r") as src:
        with open(deploy_dir / "lambda_function.py", "w") as dst:
            dst.write(src.read())
    
    # Create deployment zip
    zip_path = "lambda_bridge.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(deploy_dir / "lambda_function.py", "lambda_function.py")
    
    return zip_path

def deploy_lambda():
    """Deploy Lambda function to AWS"""
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    iam_client = boto3.client('iam', region_name='us-east-1')
    
    # Create IAM role for Lambda
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    try:
        role_response = iam_client.create_role(
            RoleName='SecurityAgentLambdaRole',
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for Security Agent Lambda Bridge'
        )
        role_arn = role_response['Role']['Arn']
        print(f"Created IAM role: {role_arn}")
        
        # Wait for role to propagate
        print("Waiting for IAM role to propagate...")
        time.sleep(10)
        
    except iam_client.exceptions.EntityAlreadyExistsException:
        role_response = iam_client.get_role(RoleName='SecurityAgentLambdaRole')
        role_arn = role_response['Role']['Arn']
        print(f"Using existing IAM role: {role_arn}")
    
    # Attach basic Lambda execution policy
    try:
        iam_client.attach_role_policy(
            RoleName='SecurityAgentLambdaRole',
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
    except:
        pass  # Policy might already be attached
    
    # Create Lambda package
    zip_path = create_lambda_package()
    
    try:
        # Read zip file
        with open(zip_path, 'rb') as f:
            zip_content = f.read()
        
        function_name = 'security-agent-bridge'
        
        # Retry Lambda creation with backoff
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Create Lambda function
                response = lambda_client.create_function(
                    FunctionName=function_name,
                    Runtime='python3.11',
                    Role=role_arn,
                    Handler='lambda_function.lambda_handler',
                    Code={'ZipFile': zip_content},
                    Description='Bridge function between Bedrock Agent and AgentCore Gateway',
                    Timeout=30,
                    Environment={
                        'Variables': {
                            'GATEWAY_URL': 'https://security-gateway-0xd0v9msee.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp',
                            'COGNITO_CLIENT_ID': 'cga3d98ldb3hd38a6lbbjluj0',
                            'COGNITO_TOKEN_ENDPOINT': 'https://cognito-idp.us-east-1.amazonaws.com/us-east-1_DBAPV3Fct/oauth2/token',
                            'COGNITO_SCOPE': 'openid'
                        }
                    }
                )
                print(f"Created Lambda function: {response['FunctionArn']}")
                return response['FunctionArn']
                
            except lambda_client.exceptions.ResourceConflictException:
                # Update existing function
                response = lambda_client.update_function_code(
                    FunctionName=function_name,
                    ZipFile=zip_content
                )
                
                # Update environment variables
                lambda_client.update_function_configuration(
                    FunctionName=function_name,
                    Environment={
                        'Variables': {
                            'GATEWAY_URL': 'https://security-gateway-0xd0v9msee.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp',
                            'COGNITO_CLIENT_ID': 'cga3d98ldb3hd38a6lbbjluj0',
                            'COGNITO_TOKEN_ENDPOINT': 'https://cognito-idp.us-east-1.amazonaws.com/us-east-1_DBAPV3Fct/oauth2/token',
                            'COGNITO_SCOPE': 'openid'
                        }
                    }
                )
                
                print(f"Updated Lambda function: {response['FunctionArn']}")
                return response['FunctionArn']
                
            except Exception as e:
                if "cannot be assumed by Lambda" in str(e) and attempt < max_retries - 1:
                    print(f"Attempt {attempt + 1} failed, retrying in 10 seconds...")
                    time.sleep(10)
                    continue
                else:
                    raise e
        
    finally:
        # Cleanup
        if os.path.exists(zip_path):
            os.remove(zip_path)
        if os.path.exists("lambda_deploy"):
            import shutil
            shutil.rmtree("lambda_deploy")

if __name__ == "__main__":
    try:
        function_arn = deploy_lambda()
        print(f"\n✅ Lambda bridge deployed successfully!")
        print(f"Function ARN: {function_arn}")
    except Exception as e:
        print(f"\n❌ Lambda deployment failed: {e}")
