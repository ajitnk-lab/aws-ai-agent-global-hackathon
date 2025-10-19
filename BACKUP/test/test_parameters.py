#!/usr/bin/env python3
import boto3
import uuid

def test_parameter_queries():
    bedrock_runtime = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
    agent_id = "KS91Z9H2MA"
    agent_alias_id = "UEWYRHGIEL"
    
    # Test specific parameter queries
    queries = [
        "Get only medium risk findings from SecurityHub in us-east-1 region only",
        "Check security services configuration for us-west-2 region",
        "Analyze security posture for EC2 service with recommendations included",
        "Get high severity findings, limit to 3 results"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'='*70}")
        print(f"Parameter Test {i}: {query}")
        print('='*70)
        
        try:
            session_id = str(uuid.uuid4())
            response = bedrock_runtime.invoke_agent(
                agentId=agent_id,
                agentAliasId=agent_alias_id,
                sessionId=session_id,
                inputText=query
            )
            
            response_text = ""
            for event in response['completion']:
                if 'chunk' in event:
                    chunk = event['chunk']
                    if 'bytes' in chunk:
                        response_text += chunk['bytes'].decode('utf-8')
            
            print(f"Response:\n{response_text}")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_parameter_queries()
