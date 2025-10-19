#!/usr/bin/env python3
import boto3
import json

def test_lambda_parameters():
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Test different parameter combinations
    test_cases = [
        {
            'name': 'Medium risk findings in us-east-1',
            'event': {
                'actionGroup': 'security-tools',
                'function': 'getSecurityFindings',
                'parameters': [
                    {'name': 'severity', 'value': 'MEDIUM'},
                    {'name': 'region', 'value': 'us-east-1'},
                    {'name': 'limit', 'value': '5'}
                ]
            }
        },
        {
            'name': 'Security services in us-west-2',
            'event': {
                'actionGroup': 'security-tools',
                'function': 'checkSecurityServices',
                'parameters': [
                    {'name': 'region', 'value': 'us-west-2'}
                ]
            }
        },
        {
            'name': 'Security posture with recommendations',
            'event': {
                'actionGroup': 'security-tools',
                'function': 'analyzeSecurityPosture',
                'parameters': [
                    {'name': 'include_recommendations', 'value': 'true'},
                    {'name': 'service', 'value': 'EC2'}
                ]
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{'='*60}")
        print(f"Test: {test_case['name']}")
        print('='*60)
        
        try:
            response = lambda_client.invoke(
                FunctionName='security-agent-bridge',
                Payload=json.dumps(test_case['event'])
            )
            
            result = json.loads(response['Payload'].read())
            
            # Extract the actual response body
            if 'functionResponse' in result and 'responseBody' in result['functionResponse']:
                body = result['functionResponse']['responseBody']['TEXT']['body']
                parsed_body = json.loads(body)
                print(f"Parameters received: {parsed_body.get('parameters_received', 'N/A')}")
                print(f"Response: {json.dumps(parsed_body, indent=2)}")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_lambda_parameters()
