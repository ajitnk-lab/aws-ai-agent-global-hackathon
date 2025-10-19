#!/usr/bin/env python3
import boto3
import zipfile
import os
from pathlib import Path

def update_lambda_bedrock():
    """Update Lambda with proper Bedrock Agent format"""
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Create deployment directory
    deploy_dir = Path("lambda_deploy_bedrock")
    deploy_dir.mkdir(exist_ok=True)
    
    # Copy Bedrock-formatted Lambda function
    with open("lambda_bridge_bedrock_format.py", "r") as src:
        with open(deploy_dir / "lambda_function.py", "w") as dst:
            dst.write(src.read())
    
    # Create deployment zip
    zip_path = "lambda_bridge_bedrock.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(deploy_dir / "lambda_function.py", "lambda_function.py")
    
    try:
        # Read zip file
        with open(zip_path, 'rb') as f:
            zip_content = f.read()
        
        # Update Lambda function
        response = lambda_client.update_function_code(
            FunctionName='security-agent-bridge',
            ZipFile=zip_content
        )
        
        print(f"Updated Lambda: {response['FunctionArn']}")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    finally:
        # Cleanup
        if os.path.exists(zip_path):
            os.remove(zip_path)
        if os.path.exists("lambda_deploy_bedrock"):
            import shutil
            shutil.rmtree("lambda_deploy_bedrock")

if __name__ == "__main__":
    if update_lambda_bedrock():
        print("✅ Lambda updated with proper Bedrock format!")
    else:
        print("❌ Lambda update failed!")
