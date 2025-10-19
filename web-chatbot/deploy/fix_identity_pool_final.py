#!/usr/bin/env python3
import boto3
import json

def fix_identity_pool_final():
    """Create new Identity Pool with proper session policy"""
    
    cognito_identity = boto3.client('cognito-identity', region_name='us-east-1')
    iam = boto3.client('iam', region_name='us-east-1')
    
    old_pool_id = 'us-east-1:1fb527be-a746-41c6-b345-a98228a0abc4'
    
    try:
        # Delete old identity pool
        try:
            cognito_identity.delete_identity_pool(IdentityPoolId=old_pool_id)
            print("✅ Deleted old identity pool")
        except:
            pass
        
        # Create new identity pool
        new_pool = cognito_identity.create_identity_pool(
            IdentityPoolName='AgentCoreSecurityChatbotFixed',
            AllowUnauthenticatedIdentities=True
        )
        
        new_pool_id = new_pool['IdentityPoolId']
        print(f"✅ Created new identity pool: {new_pool_id}")
        
        # Create new role with session policy
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Federated": "cognito-identity.amazonaws.com"
                    },
                    "Action": "sts:AssumeRoleWithWebIdentity",
                    "Condition": {
                        "StringEquals": {
                            "cognito-identity.amazonaws.com:aud": new_pool_id
                        },
                        "ForAnyValue:StringLike": {
                            "cognito-identity.amazonaws.com:amr": "unauthenticated"
                        }
                    }
                }
            ]
        }
        
        # Delete old role
        try:
            iam.delete_role_policy(
                RoleName='AgentCoreSecurityChatbot_Unauth_Role',
                PolicyName='BedrockAgentAccessFixed'
            )
            iam.delete_role(RoleName='AgentCoreSecurityChatbot_Unauth_Role')
        except:
            pass
        
        # Create new role
        new_role_name = 'AgentCoreSecurityChatbot_Fixed_Role'
        role_response = iam.create_role(
            RoleName=new_role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Fixed role for Bedrock Agent access'
        )
        
        role_arn = role_response['Role']['Arn']
        print(f"✅ Created new role: {role_arn}")
        
        # Add inline policy
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
        
        iam.put_role_policy(
            RoleName=new_role_name,
            PolicyName='BedrockAccess',
            PolicyDocument=json.dumps(policy_document)
        )
        print("✅ Added Bedrock policy to role")
        
        # Set identity pool roles
        cognito_identity.set_identity_pool_roles(
            IdentityPoolId=new_pool_id,
            Roles={
                'unauthenticated': role_arn
            }
        )
        print("✅ Set identity pool roles")
        
        return new_pool_id
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    new_pool_id = fix_identity_pool_final()
    if new_pool_id:
        print(f"\n🎉 New Identity Pool created: {new_pool_id}")
        print("\n🔧 UPDATE REQUIRED:")
        print("Update your React app with the new Identity Pool ID:")
        print(f"identityPoolId: '{new_pool_id}'")
    else:
        print("\n💥 Failed to create new identity pool")
