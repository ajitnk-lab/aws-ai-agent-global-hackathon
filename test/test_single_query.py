#!/usr/bin/env python3
import boto3
import uuid

def test_single_query():
    bedrock_runtime = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
    agent_id = "KS91Z9H2MA"
    agent_alias_id = "UEWYRHGIEL"
    
    query = "list 1 security hub finding from us-east-1 region of high risk"
    
    print(f"Query: {query}")
    print('='*60)
    
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
        
        print("✅ SUCCESS!")
        print(f"Response:\n{response_text}")
        
    except Exception as e:
        print(f"❌ FAILED: {e}")

if __name__ == "__main__":
    test_single_query()
