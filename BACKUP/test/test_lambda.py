#!/usr/bin/env python3
import boto3
import json

def test_lambda():
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    test_event = {
        'actionGroup': 'security-tools',
        'function': 'checkSecurityServices',
        'parameters': [
            {'name': 'region', 'value': 'us-east-1'}
        ]
    }
    
    response = lambda_client.invoke(
        FunctionName='security-agent-bridge',
        Payload=json.dumps(test_event)
    )
    
    result = json.loads(response['Payload'].read())
    print("Lambda Response:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test_lambda()
