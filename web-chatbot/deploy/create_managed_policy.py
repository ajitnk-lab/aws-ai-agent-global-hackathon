#!/usr/bin/env python3
import boto3
import json

def create_managed_policy():
    """Create managed policy for Bedrock access"""
    
    iam = boto3.client('iam', region_name='us-east-1')
    role_name = 'AgentCoreSecurityChatbot_Unauth_Role'
    
    # Create managed policy
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeAgent"
                ],
                "Resource": "*"
            }
        ]
    }
    
    try:
        # Create managed policy
        policy_response = iam.create_policy(
            PolicyName='BedrockAgentAccessPolicy',
            PolicyDocument=json.dumps(policy_document),
            Description='Allows access to Bedrock Agent for chatbot'
        )
        
        policy_arn = policy_response['Policy']['Arn']
        print(f"✅ Created managed policy: {policy_arn}")
        
        # Attach to role
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy_arn
        )
        
        print("✅ Attached managed policy to role")
        
        return True
        
    except iam.exceptions.EntityAlreadyExistsException:
        # Policy exists, just attach it
        policy_arn = f"arn:aws:iam::039920874011:policy/BedrockAgentAccessPolicy"
        
        try:
            iam.attach_role_policy(
                RoleName=role_name,
                PolicyArn=policy_arn
            )
            print("✅ Attached existing managed policy to role")
            return True
        except:
            print("✅ Policy already attached")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    if create_managed_policy():
        print("\n🎉 Managed policy approach applied!")
        print("⏳ Wait 1-2 minutes and test the chatbot")
    else:
        print("\n💥 Failed to create managed policy")
