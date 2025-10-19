#!/usr/bin/env python3
"""
Final test of Bedrock Agent to verify findings count
"""
import boto3
import json
import time

def test_bedrock_agent():
    """Test the Bedrock Agent directly"""
    try:
        print("Testing Bedrock Agent Security Findings Count")
        print("=" * 60)
        
        # Create Bedrock Agent Runtime client
        client = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
        
        # Test queries
        queries = [
            "How many security findings do we have in total?",
            "Get all security findings from Security Hub",
            "Call get_security_findings with no parameters to get all findings"
        ]
        
        for i, query in enumerate(queries, 1):
            print(f"\n{i}. Testing query: '{query}'")
            print("-" * 50)
            
            try:
                response = client.invoke_agent(
                    agentId='KS91Z9H2MA',
                    agentAliasId='TSTALIASID',
                    sessionId=f'test-session-{int(time.time())}-{i}',
                    inputText=query
                )
                
                # Process streaming response
                full_response = ""
                for event in response['completion']:
                    if 'chunk' in event:
                        chunk = event['chunk']
                        if 'bytes' in chunk:
                            text = chunk['bytes'].decode('utf-8')
                            full_response += text
                
                print(f"Response: {full_response[:500]}...")
                
                # Look for findings count in response
                if "findings" in full_response.lower():
                    lines = full_response.split('\n')
                    for line in lines:
                        if any(word in line.lower() for word in ['total', 'findings', 'count', 'number']):
                            print(f"Key line: {line.strip()}")
                
                # Wait between requests
                if i < len(queries):
                    print("⏳ Waiting 10 seconds to avoid rate limiting...")
                    time.sleep(10)
                    
            except Exception as e:
                print(f"Error with query {i}: {e}")
        
        print("\n" + "=" * 60)
        print("Bedrock Agent test completed!")
        
    except Exception as e:
        print(f"Error testing Bedrock Agent: {e}")

if __name__ == "__main__":
    test_bedrock_agent()
