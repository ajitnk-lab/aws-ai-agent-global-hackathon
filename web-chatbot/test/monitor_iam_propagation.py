#!/usr/bin/env python3
import boto3
import time
from datetime import datetime

def test_bedrock_access():
    """Test Bedrock Agent access"""
    cognito_identity = boto3.client('cognito-identity', region_name='us-east-1')
    identity_pool_id = 'us-east-1:1fb527be-a746-41c6-b345-a98228a0abc4'
    
    try:
        # Get credentials
        identity_response = cognito_identity.get_id(IdentityPoolId=identity_pool_id)
        credentials_response = cognito_identity.get_credentials_for_identity(
            IdentityId=identity_response['IdentityId']
        )
        
        credentials = credentials_response['Credentials']
        
        # Test Bedrock access
        bedrock_client = boto3.client(
            'bedrock-agent-runtime',
            region_name='us-east-1',
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretKey'],
            aws_session_token=credentials['SessionToken']
        )
        
        response = bedrock_client.invoke_agent(
            agentId='KS91Z9H2MA',
            agentAliasId='UEWYRHGIEL',
            sessionId='monitor-test',
            inputText='Hello'
        )
        
        return True, "SUCCESS"
        
    except Exception as e:
        if 'not authorized' in str(e):
            return False, "STILL_PROPAGATING"
        else:
            return False, f"ERROR: {str(e)[:100]}"

def monitor_propagation():
    """Monitor IAM propagation every 5 minutes"""
    
    start_time = datetime.now()
    attempt = 1
    
    print("🔄 Monitoring IAM Policy Propagation")
    print("=" * 50)
    print(f"Started at: {start_time.strftime('%H:%M:%S')}")
    print("Checking every 5 minutes...")
    print()
    
    while attempt <= 6:  # Monitor for 30 minutes max
        current_time = datetime.now()
        elapsed = (current_time - start_time).total_seconds() / 60
        
        print(f"⏰ Check #{attempt} at {current_time.strftime('%H:%M:%S')} ({elapsed:.1f} min elapsed)")
        
        success, message = test_bedrock_access()
        
        if success:
            print("🎉 SUCCESS! IAM policies have propagated!")
            print("✅ Bedrock Agent access is now working")
            print(f"🌐 Chatbot is ready: https://dwtz1c6gg4gdx.cloudfront.net")
            print(f"⏱️  Total propagation time: {elapsed:.1f} minutes")
            return True
        else:
            if message == "STILL_PROPAGATING":
                print("⏳ Still propagating... (authorization error)")
            else:
                print(f"❌ {message}")
        
        if attempt < 6:
            print("   Waiting 5 minutes for next check...\n")
            time.sleep(300)  # 5 minutes
        
        attempt += 1
    
    print("⚠️  Monitoring complete. If still not working, there may be a configuration issue.")
    return False

if __name__ == "__main__":
    monitor_propagation()
