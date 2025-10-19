"""
Deploy Lambda bridge function for Bedrock Agent to Gateway communication
"""
import boto3
import json
import zipfile
import os
import uuid
from pathlib import Path

def create_lambda_package():
    """Create Lambda deployment package"""
    
    # Create temporary directory for package
    package_dir = Path('/tmp/lambda_package')
    package_dir.mkdir(exist_ok=True)
    
    # Copy Lambda function code
    with open('lambda_bridge.py', 'r') as src:
        with open(package_dir / 'lambda_function.py', 'w') as dst:
            # Rename handler function
            content = src.read().replace('def lambda_handler', 'def lambda_handler')
            dst.write(content)
    
    # Create requirements.txt for Lambda layer
    requirements = [
        'httpx==0.25.0',
        'asyncio'
    ]
    
    with open(package_dir / 'requirements.txt', 'w') as f:
        f.write('\n'.join(requirements))
    
    # Create ZIP package
    zip_path = '/tmp/lambda_bridge.zip'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in package_dir.rglob('*'):
            if file_path.is_file():
                zipf.write(file_path, file_path.relative_to(package_dir))
    
    return zip_path

def deploy_lambda_function():
    """Deploy Lambda bridge function"""
    
    region = os.getenv('AWS_REGION', 'us-east-1')
    
    # Load Gateway configuration
    try:
        with open('../gateway/gateway_config.json', 'r') as f:
            gateway_config = json.load(f)
    except FileNotFoundError:
        print("❌ Gateway configuration not found. Deploy Gateway first.")
        return None
    
    lambda_client = boto3.client('lambda', region_name=region)
    iam = boto3.client('iam', region_name=region)
    
    # Create IAM role for Lambda
    print("1. Creating IAM role for Lambda...")
    
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    role_name = f"BedrockGatewayBridge-{uuid.uuid4().hex[:8]}"
    
    try:
        role_response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="IAM role for Bedrock Agent to AgentCore Gateway bridge"
        )
        
        # Attach basic Lambda execution policy
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
        
        role_arn = role_response['Role']['Arn']
        print(f"✅ IAM role created: {role_arn}")
        
    except iam.exceptions.EntityAlreadyExistsException:
        account_id = boto3.client('sts').get_caller_identity()['Account']
        role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"
        print(f"✅ Using existing IAM role: {role_arn}")
    
    # Create Lambda package
    print("2. Creating Lambda deployment package...")
    zip_path = create_lambda_package()
    print("✅ Lambda package created")
    
    # Deploy Lambda function
    print("3. Deploying Lambda function...")
    
    function_name = f"bedrock-agentcore-bridge-{uuid.uuid4().hex[:8]}"
    
    with open(zip_path, 'rb') as zip_file:
        zip_content = zip_file.read()
    
    lambda_response = lambda_client.create_function(
        FunctionName=function_name,
        Runtime='python3.11',
        Role=role_arn,
        Handler='lambda_function.lambda_handler',
        Code={'ZipFile': zip_content},
        Description='Bridge function for Bedrock Agent to AgentCore Gateway',
        Timeout=30,
        MemorySize=256,
        Environment={
            'Variables': {
                'GATEWAY_URL': gateway_config['gateway_url'],
                'COGNITO_CLIENT_ID': gateway_config['cognito_client_id'],
                'COGNITO_CLIENT_SECRET': gateway_config['cognito_client_secret'],
                'COGNITO_TOKEN_ENDPOINT': gateway_config['cognito_token_endpoint'],
                'COGNITO_SCOPE': gateway_config['cognito_scope']
            }
        }
    )
    
    lambda_arn = lambda_response['FunctionArn']
    print(f"✅ Lambda function deployed: {lambda_arn}")
    
    # Add resource-based policy for Bedrock Agent
    print("4. Configuring Lambda permissions...")
    
    try:
        lambda_client.add_permission(
            FunctionName=function_name,
            StatementId='bedrock-agent-invoke',
            Action='lambda:InvokeFunction',
            Principal='bedrock.amazonaws.com',
            SourceAccount=boto3.client('sts').get_caller_identity()['Account']
        )
        print("✅ Lambda permissions configured")
    except lambda_client.exceptions.ResourceConflictException:
        print("✅ Lambda permissions already configured")
    
    # Save configuration
    config = {
        "function_name": function_name,
        "function_arn": lambda_arn,
        "role_arn": role_arn,
        "gateway_config": gateway_config
    }
    
    with open('lambda_bridge_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    # Set environment variable for Bedrock Agent deployment
    os.environ['LAMBDA_BRIDGE_ARN'] = lambda_arn
    
    print("✅ Lambda bridge deployment complete!")
    print(f"   Function Name: {function_name}")
    print(f"   Function ARN: {lambda_arn}")
    print(f"   Configuration saved to: lambda_bridge_config.json")
    
    return config

if __name__ == "__main__":
    config = deploy_lambda_function()
    if config:
        print(f"\n🎯 Lambda ARN: {config['function_arn']}")
        print("Lambda bridge is ready for Bedrock Agent integration!")
