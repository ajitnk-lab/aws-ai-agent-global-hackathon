#!/usr/bin/env python3
import boto3
import json

def fix_iam_policy():
    """Fix IAM policy for Bedrock Agent access"""
    
    iam = boto3.client('iam', region_name='us-east-1')
    role_name = 'AgentCoreSecurityChatbot_Unauth_Role'
    
    # Correct policy for Bedrock Agent access
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeAgent"
                ],
                "Resource": [
                    "arn:aws:bedrock:us-east-1:039920874011:agent/KS91Z9H2MA",
                    "arn:aws:bedrock:us-east-1:039920874011:agent-alias/KS91Z9H2MA/UEWYRHGIEL"
                ]
            }
        ]
    }
    
    try:
        # Update the policy
        iam.put_role_policy(
            RoleName=role_name,
            PolicyName='BedrockAgentAccess',
            PolicyDocument=json.dumps(policy_document)
        )
        
        print("✅ Fixed IAM policy for Bedrock Agent access")
        print("✅ Added permissions for both agent and agent-alias resources")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing IAM policy: {e}")
        return False

if __name__ == "__main__":
    if fix_iam_policy():
        print("\n🎉 IAM policy fixed!")
        print("🔄 Please wait 1-2 minutes for policy changes to propagate")
        print("🌐 Then test the chatbot at: https://dwtz1c6gg4gdx.cloudfront.net")
    else:
        print("\n💥 Failed to fix IAM policy")
