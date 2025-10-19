#!/usr/bin/env python3
import boto3

def test_new_identity_pool():
    """Test new Identity Pool configuration"""
    
    cognito_identity = boto3.client('cognito-identity', region_name='us-east-1')
    new_pool_id = 'us-east-1:6feda4ed-660d-461c-8d68-90c9ce34a15a'
    
    try:
        # Get identity and credentials
        identity_response = cognito_identity.get_id(IdentityPoolId=new_pool_id)
        identity_id = identity_response['IdentityId']
        print(f"✅ Got new identity ID: {identity_id}")
        
        credentials_response = cognito_identity.get_credentials_for_identity(
            IdentityId=identity_id
        )
        
        credentials = credentials_response['Credentials']
        print("✅ Got new temporary credentials")
        
        # Test Bedrock access
        bedrock_client = boto3.client(
            'bedrock-agent-runtime',
            region_name='us-east-1',
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretKey'],
            aws_session_token=credentials['SessionToken']
        )
        
        print("🧪 Testing Bedrock Agent access with new Identity Pool...")
        
        response = bedrock_client.invoke_agent(
            agentId='KS91Z9H2MA',
            agentAliasId='UEWYRHGIEL',
            sessionId='test-new-pool',
            inputText='Hello, test message'
        )
        
        print("🎉 SUCCESS! New Identity Pool works!")
        print("✅ Bedrock Agent access is working")
        
        # Process response
        response_text = ""
        for event in response['completion']:
            if 'chunk' in event and 'bytes' in event['chunk']:
                response_text += event['chunk']['bytes'].decode('utf-8')
        
        print(f"📝 Agent response: {response_text[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing New Identity Pool Configuration")
    print("=" * 50)
    
    if test_new_identity_pool():
        print("\n🎉 FIXED! The chatbot should now work!")
        print("🌐 Test at: https://dwtz1c6gg4gdx.cloudfront.net")
        print("⏳ Wait 2-3 minutes for CloudFront cache to update")
    else:
        print("\n❌ Still having issues")
