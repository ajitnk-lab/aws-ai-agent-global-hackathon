#!/usr/bin/env python3
"""
Update Lambda function with fixed parameter handling
"""
import boto3
import zipfile
import io

def update_lambda_function():
    """Update the Lambda function with fixed parameter handling"""
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Read the fixed Lambda code
    with open('lambda_bridge_fixed_parameters.py', 'r') as f:
        lambda_code = f.read()
    
    # Create a zip file in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    zip_buffer.seek(0)
    
    try:
        # Update the Lambda function
        response = lambda_client.update_function_code(
            FunctionName='security-agent-bridge',
            ZipFile=zip_buffer.getvalue()
        )
        
        print(f"✅ Lambda function updated successfully!")
        print(f"Function ARN: {response['FunctionArn']}")
        print(f"Last Modified: {response['LastModified']}")
        print(f"Code SHA256: {response['CodeSha256']}")
        
        return response
        
    except Exception as e:
        print(f"❌ Error updating Lambda function: {e}")
        return None

if __name__ == "__main__":
    update_lambda_function()
