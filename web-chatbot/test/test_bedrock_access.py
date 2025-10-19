#!/usr/bin/env python3
import boto3
from botocore.exceptions import ClientError
from boto3 import Session
from botocore.credentials import Credentials

def test_bedrock_access():
    """Test Bedrock Agent access with Cognito Identity Pool credentials"""
    
    # Simulate the same credentials the web app uses
    cognito_identity = boto3.client('cognito-identity', region_name='us-east-1')
    identity_pool_id = 'us-east-1:1fb527be-a746-41c6-b345-a98228a0abc4'
    
    try:
        # Get identity ID
        identity_response = cognito_identity.get_id(
            IdentityPoolId=identity_pool_id
        )
        identity_id = identity_response['IdentityId']
        print(f"✅ Got identity ID: {identity_id}")
        
        # Get credentials for identity
        credentials_response = cognito_identity.get_credentials_for_identity(
            IdentityId=identity_id
        )
        
        credentials = credentials_response['Credentials']
        print("✅ Got temporary credentials")
        
        # Create Bedrock client with these credentials
        bedrock_client = boto3.client(
            'bedrock-agent-runtime',
            region_name='us-east-1',
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretKey'],
            aws_session_token=credentials['SessionToken']
        )
        
        # Test invoke agent
        print("🧪 Testing Bedrock Agent access...")
        
        response = bedrock_client.invoke_agent(
            agentId='KS91Z9H2MA',
            agentAliasId='UEWYRHGIEL',
            sessionId='test-session-123',
            inputText='Hello, can you help me with security assessment?'
        )
        
        print("✅ Bedrock Agent access successful!")
        print("✅ IAM policy is working correctly")
        
        # Process response
        response_text = ""
        for event in response['completion']:
            if 'chunk' in event and 'bytes' in event['chunk']:
                response_text += event['chunk']['bytes'].decode('utf-8')
        
        print(f"📝 Agent response: {response_text[:100]}...")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        if 'not authorized' in error_message:
            print("❌ Still not authorized - IAM policy needs more time to propagate")
            print("⏳ Wait another 2-3 minutes and try again")
        else:
            print(f"❌ Error: {error_code} - {error_message}")
        
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Bedrock Agent access with Cognito credentials...")
    print("=" * 60)
    
    success = test_bedrock_access()
    
    if success:
        print("\n🎉 SUCCESS! The chatbot should now work!")
        print("🌐 Test it at: https://dwtz1c6gg4gdx.cloudfront.net")
    else:
        print("\n⏳ IAM policy may still be propagating. Try again in 2-3 minutes.")
