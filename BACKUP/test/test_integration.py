"""
Integration test for AgentCore Security Assessment Application
"""
import boto3
import json
import os
import asyncio
import httpx
from pathlib import Path

def load_config(config_file):
    """Load configuration from JSON file"""
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Configuration file not found: {config_file}")
        return None

async def test_gateway_direct():
    """Test direct Gateway access with OAuth"""
    print("\n🧪 Testing AgentCore Gateway (Direct Access)")
    
    gateway_config = load_config('../gateway/gateway_config.json')
    if not gateway_config:
        return False
    
    # Get OAuth token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            gateway_config['cognito_token_endpoint'],
            data={
                'grant_type': 'client_credentials',
                'client_id': gateway_config['cognito_client_id'],
                'client_secret': gateway_config['cognito_client_secret'],
                'scope': gateway_config['cognito_scope']
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        if token_response.status_code != 200:
            print(f"❌ OAuth token request failed: {token_response.text}")
            return False
        
        token = token_response.json()['access_token']
        print("✅ OAuth token obtained")
        
        # Test security services check
        gateway_response = await client.post(
            gateway_config['gateway_url'],
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "check_security_services",
                    "arguments": {}
                }
            }
        )
        
        if gateway_response.status_code == 200:
            result = gateway_response.json()
            if 'result' in result:
                print("✅ Gateway security services check successful")
                return True
            else:
                print(f"❌ Gateway returned error: {result}")
                return False
        else:
            print(f"❌ Gateway request failed: {gateway_response.status_code}")
            return False

def test_bedrock_agent():
    """Test Bedrock Agent invocation"""
    print("\n🧪 Testing Bedrock Agent")
    
    bedrock_config = load_config('../bedrock/bedrock_agent_config.json')
    if not bedrock_config:
        return False
    
    region = os.getenv('AWS_REGION', 'us-east-1')
    bedrock_runtime = boto3.client('bedrock-agent-runtime', region_name=region)
    
    try:
        # Test agent invocation
        response = bedrock_runtime.invoke_agent(
            agentId=bedrock_config['agent_id'],
            agentAliasId='TSTALIASID',  # Test alias
            sessionId='test-session-123',
            inputText="Check the status of AWS security services in my account"
        )
        
        # Process streaming response
        event_stream = response['completion']
        full_response = ""
        
        for event in event_stream:
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    full_response += chunk['bytes'].decode('utf-8')
        
        if full_response:
            print("✅ Bedrock Agent responded successfully")
            print(f"   Response preview: {full_response[:200]}...")
            return True
        else:
            print("❌ Bedrock Agent returned empty response")
            return False
            
    except Exception as e:
        print(f"❌ Bedrock Agent test failed: {str(e)}")
        return False

def test_lambda_bridge():
    """Test Lambda bridge function"""
    print("\n🧪 Testing Lambda Bridge Function")
    
    lambda_config = load_config('../bedrock/lambda_bridge_config.json')
    if not lambda_config:
        return False
    
    region = os.getenv('AWS_REGION', 'us-east-1')
    lambda_client = boto3.client('lambda', region_name=region)
    
    try:
        # Test Lambda function
        test_event = {
            "actionGroup": "SecurityAssessmentTools",
            "function": "checkSecurityServices",
            "parameters": []
        }
        
        response = lambda_client.invoke(
            FunctionName=lambda_config['function_name'],
            Payload=json.dumps(test_event)
        )
        
        result = json.loads(response['Payload'].read())
        
        if 'functionResponse' in result:
            print("✅ Lambda bridge function working")
            return True
        else:
            print(f"❌ Lambda bridge returned unexpected result: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Lambda bridge test failed: {str(e)}")
        return False

def test_memory_integration():
    """Test AgentCore Memory integration"""
    print("\n🧪 Testing AgentCore Memory")
    
    memory_id = os.getenv('BEDROCK_AGENTCORE_MEMORY_ID')
    if not memory_id:
        print("❌ BEDROCK_AGENTCORE_MEMORY_ID not set")
        return False
    
    try:
        from bedrock_agentcore.memory import MemoryClient
        
        region = os.getenv('AWS_REGION', 'us-east-1')
        client = MemoryClient(region_name=region)
        
        # Test memory creation
        client.create_event(
            memory_id=memory_id,
            actor_id="test_user",
            session_id="test_session",
            messages=[("Test security assessment memory", "user")]
        )
        
        print("✅ Memory integration working")
        return True
        
    except Exception as e:
        print(f"❌ Memory test failed: {str(e)}")
        return False

async def run_integration_tests():
    """Run all integration tests"""
    print("🚀 Starting AgentCore Security Assessment Integration Tests")
    print("="*60)
    
    tests = [
        ("Memory Integration", test_memory_integration),
        ("Gateway Direct Access", test_gateway_direct),
        ("Lambda Bridge", test_lambda_bridge),
        ("Bedrock Agent", test_bedrock_agent)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {str(e)}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("🎯 INTEGRATION TEST RESULTS")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed! Your AgentCore Security Assessment Application is ready.")
    else:
        print("⚠️  Some tests failed. Check the configuration and deployment.")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(run_integration_tests())
    exit(0 if success else 1)
