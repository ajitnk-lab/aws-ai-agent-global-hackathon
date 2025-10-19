#!/usr/bin/env python3
import boto3
import uuid
import time

def test_fixed_function_calls():
    bedrock_runtime = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
    agent_id = "KS91Z9H2MA"
    agent_alias_id = "UEWYRHGIEL"
    
    # Test queries with varied parameters
    test_queries = [
        {
            "query": "Check security services configuration for us-west-2 region",
            "expected_params": ["region: us-west-2"]
        },
        {
            "query": "Get medium severity security findings, limit to 3 results",
            "expected_params": ["severity: MEDIUM", "limit: 3"]
        },
        {
            "query": "Analyze security posture for EC2 service with recommendations included",
            "expected_params": ["service: EC2", "include_recommendations: true"]
        },
        {
            "query": "Get high severity findings from us-east-1 region only",
            "expected_params": ["severity: HIGH", "region: us-east-1"]
        }
    ]
    
    results = []
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n{'='*70}")
        print(f"Test {i}: {test['query']}")
        print(f"Expected params: {', '.join(test['expected_params'])}")
        print('='*70)
        
        try:
            session_id = str(uuid.uuid4())
            response = bedrock_runtime.invoke_agent(
                agentId=agent_id,
                agentAliasId=agent_alias_id,
                sessionId=session_id,
                inputText=test['query']
            )
            
            response_text = ""
            for event in response['completion']:
                if 'chunk' in event:
                    chunk = event['chunk']
                    if 'bytes' in chunk:
                        response_text += chunk['bytes'].decode('utf-8')
            
            print(f"✅ SUCCESS")
            print(f"Response: {response_text[:200]}...")
            
            results.append({
                'test': i,
                'query': test['query'],
                'status': 'SUCCESS',
                'response_length': len(response_text)
            })
            
        except Exception as e:
            print(f"❌ FAILED: {e}")
            results.append({
                'test': i,
                'query': test['query'],
                'status': 'FAILED',
                'error': str(e)
            })
        
        time.sleep(2)
    
    # Summary
    print(f"\n{'='*70}")
    print("TEST SUMMARY")
    print('='*70)
    
    passed = sum(1 for r in results if r['status'] == 'SUCCESS')
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    
    return results

if __name__ == "__main__":
    test_fixed_function_calls()
