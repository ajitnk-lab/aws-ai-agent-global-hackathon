#!/usr/bin/env python3
import boto3
import json

def test_authenticated_access():
    """Test authenticated Cognito access to Bedrock Agent"""
    
    cognito_idp = boto3.client('cognito-idp', region_name='us-east-1')
    cognito_identity = boto3.client('cognito-identity', region_name='us-east-1')
    
    try:
        # Authenticate user
        auth_response = cognito_idp.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            ClientId='613pomsjrqs8om564unnl6nutv',
            AuthParameters={
                'USERNAME': 'chatbot-user',
                'PASSWORD': 'ChatbotPass123!'
            }
        )
        
        id_token = auth_response['AuthenticationResult']['IdToken']
        print("✅ User authenticated successfully")
        
        # Get identity with token
        identity_response = cognito_identity.get_id(
            IdentityPoolId='us-east-1:6feda4ed-660d-461c-8d68-90c9ce34a15a',
            Logins={
                'cognito-idp.us-east-1.amazonaws.com/us-east-1_W9Ro1YsQX': id_token
            }
        )
        
        identity_id = identity_response['IdentityId']
        print(f"✅ Got authenticated identity: {identity_id}")
        
        # Get credentials for authenticated identity
        credentials_response = cognito_identity.get_credentials_for_identity(
            IdentityId=identity_id,
            Logins={
                'cognito-idp.us-east-1.amazonaws.com/us-east-1_W9Ro1YsQX': id_token
            }
        )
        
        credentials = credentials_response['Credentials']
        print("✅ Got authenticated credentials")
        
        # Test Bedrock access
        bedrock_client = boto3.client(
            'bedrock-agent-runtime',
            region_name='us-east-1',
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretKey'],
            aws_session_token=credentials['SessionToken']
        )
        
        print("🧪 Testing Bedrock Agent access with authenticated credentials...")
        
        response = bedrock_client.invoke_agent(
            agentId='KS91Z9H2MA',
            agentAliasId='UEWYRHGIEL',
            sessionId='auth-test-session',
            inputText='Hello, can you help me with security assessment?'
        )
        
        print("🎉 SUCCESS! Authenticated access works!")
        
        # Process response
        response_text = ""
        for event in response['completion']:
            if 'chunk' in event and 'bytes' in event['chunk']:
                response_text += event['chunk']['bytes'].decode('utf-8')
        
        print(f"📝 Agent response: {response_text[:150]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Authenticated Cognito Access")
    print("=" * 50)
    
    if test_authenticated_access():
        print("\n🎉 AUTHENTICATION FIXED!")
        print("✅ Chatbot will now work with authenticated users")
        print("🌐 Test at: https://dwtz1c6gg4gdx.cloudfront.net")
        print("🔐 Auto-login: chatbot-user / ChatbotPass123!")
    else:
        print("\n❌ Authentication still not working")
