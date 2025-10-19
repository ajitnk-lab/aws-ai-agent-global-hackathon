#!/usr/bin/env python3
"""
Deploy parameter-aware Lambda function
"""
import zipfile
import boto3
import os

def deploy_parameter_aware():
    """Deploy the parameter-aware Lambda function"""
    
    # Create zip file
    zip_filename = '../lambda-parameter-aware.zip'
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write('lambda_bridge_parameter_aware.py', 'lambda_function.py')
    
    print(f"✅ Created {zip_filename}")
    
    # Update Lambda function
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    with open(zip_filename, 'rb') as zip_file:
        response = lambda_client.update_function_code(
            FunctionName='security-agent-bridge',
            ZipFile=zip_file.read()
        )
    
    print(f"✅ Updated Lambda function: {response['FunctionName']}")
    print(f"   Last Modified: {response['LastModified']}")
    print(f"   Code SHA256: {response['CodeSha256']}")
    
    # Clean up
    os.remove(zip_filename)
    print(f"✅ Cleaned up {zip_filename}")

if __name__ == "__main__":
    deploy_parameter_aware()
