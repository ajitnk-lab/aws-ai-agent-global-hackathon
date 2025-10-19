#!/usr/bin/env python3
import boto3
import json

def fix_iam_policy_broader():
    """Fix IAM policy with broader Bedrock permissions"""
    
    iam = boto3.client('iam', region_name='us-east-1')
    role_name = 'AgentCoreSecurityChatbot_Unauth_Role'
    
    # Broader policy for Bedrock access
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeAgent",
                    "bedrock:Retrieve",
                    "bedrock:RetrieveAndGenerate"
                ],
                "Resource": "*"
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
        
        print("✅ Updated IAM policy with broader Bedrock permissions")
        print("✅ Using wildcard resource for maximum compatibility")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating IAM policy: {e}")
        return False

if __name__ == "__main__":
    if fix_iam_policy_broader():
        print("\n🎉 IAM policy updated with broader permissions!")
        print("🔄 Please wait 1-2 minutes for policy changes to propagate")
    else:
        print("\n💥 Failed to update IAM policy")
