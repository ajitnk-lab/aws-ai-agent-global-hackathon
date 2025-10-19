#!/usr/bin/env python3
import boto3
import json

def fix_cognito_identity_pool():
    """Fix Cognito Identity Pool policy directly"""
    
    cognito_identity = boto3.client('cognito-identity', region_name='us-east-1')
    iam = boto3.client('iam', region_name='us-east-1')
    
    identity_pool_id = 'us-east-1:1fb527be-a746-41c6-b345-a98228a0abc4'
    role_name = 'AgentCoreSecurityChatbot_Unauth_Role'
    
    try:
        # Create a new policy with session policy format
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
        
        # Delete and recreate the role policy
        try:
            iam.delete_role_policy(
                RoleName=role_name,
                PolicyName='BedrockAgentAccess'
            )
        except:
            pass
        
        # Create new policy
        iam.put_role_policy(
            RoleName=role_name,
            PolicyName='BedrockAgentAccessFixed',
            PolicyDocument=json.dumps(policy_document)
        )
        
        print("✅ Updated IAM role policy")
        
        # Also try updating identity pool roles again
        role_arn = f"arn:aws:iam::039920874011:role/{role_name}"
        
        cognito_identity.set_identity_pool_roles(
            IdentityPoolId=identity_pool_id,
            Roles={
                'unauthenticated': role_arn
            },
            RoleMappings={}
        )
        
        print("✅ Refreshed identity pool role mapping")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    if fix_cognito_identity_pool():
        print("\n🎉 Cognito Identity Pool policy fixed!")
        print("⏳ Wait 2-3 minutes for changes to propagate")
        print("🌐 Test at: https://dwtz1c6gg4gdx.cloudfront.net")
    else:
        print("\n💥 Failed to fix policy")
