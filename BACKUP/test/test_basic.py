#!/usr/bin/env python3
import boto3
import uuid

def test_basic():
    bedrock_runtime = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
    agent_id = "KS91Z9H2MA"
    agent_alias_id = "UEWYRHGIEL"
    
    # Test basic conversation
    session_id = str(uuid.uuid4())
    response = bedrock_runtime.invoke_agent(
        agentId=agent_id,
        agentAliasId=agent_alias_id,
        sessionId=session_id,
        inputText="Hello, what can you help me with?"
    )
    
    response_text = ""
    for event in response['completion']:
        if 'chunk' in event:
            chunk = event['chunk']
            if 'bytes' in chunk:
                response_text += chunk['bytes'].decode('utf-8')
    
    print("Basic Response:")
    print(response_text)

if __name__ == "__main__":
    test_basic()
