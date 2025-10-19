#!/usr/bin/env python3
import boto3
import json

def create_cognito_identity_pool():
    """Create Cognito Identity Pool for unauthenticated access to Bedrock Agent"""
    
    cognito_identity = boto3.client('cognito-identity', region_name='us-east-1')
    iam = boto3.client('iam', region_name='us-east-1')
    
    try:
        # Create Identity Pool
        identity_pool = cognito_identity.create_identity_pool(
            IdentityPoolName='AgentCoreSecurityChatbot',
            AllowUnauthenticatedIdentities=True
        )
        
        identity_pool_id = identity_pool['IdentityPoolId']
        print(f"✅ Created Identity Pool: {identity_pool_id}")
        
        # Create IAM role for unauthenticated users
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
                            "cognito-identity.amazonaws.com:aud": identity_pool_id
                        },
                        "ForAnyValue:StringLike": {
                            "cognito-identity.amazonaws.com:amr": "unauthenticated"
                        }
                    }
                }
            ]
        }
        
        # Create role
        role_name = 'AgentCoreSecurityChatbot_Unauth_Role'
        try:
            role_response = iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description='Role for unauthenticated users to access Bedrock Agent'
            )
            role_arn = role_response['Role']['Arn']
            print(f"✅ Created IAM role: {role_arn}")
        except iam.exceptions.EntityAlreadyExistsException:
            role_response = iam.get_role(RoleName=role_name)
            role_arn = role_response['Role']['Arn']
            print(f"✅ Using existing IAM role: {role_arn}")
        
        # Attach policy for Bedrock Agent access
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "bedrock:InvokeAgent"
                    ],
                    "Resource": f"arn:aws:bedrock:us-east-1:*:agent/KS91Z9H2MA"
                }
            ]
        }
        
        try:
            iam.put_role_policy(
                RoleName=role_name,
                PolicyName='BedrockAgentAccess',
                PolicyDocument=json.dumps(policy_document)
            )
            print("✅ Attached Bedrock Agent access policy")
        except:
            pass
        
        # Set identity pool roles
        cognito_identity.set_identity_pool_roles(
            IdentityPoolId=identity_pool_id,
            Roles={
                'unauthenticated': role_arn
            }
        )
        print("✅ Set identity pool roles")
        
        return identity_pool_id
        
    except Exception as e:
        print(f"❌ Error creating Cognito Identity Pool: {e}")
        return None

if __name__ == "__main__":
    identity_pool_id = create_cognito_identity_pool()
    if identity_pool_id:
        print(f"\n🎉 Cognito Identity Pool created successfully!")
        print(f"Identity Pool ID: {identity_pool_id}")
        print(f"\nUpdate your React app with this Identity Pool ID:")
        print(f"identityPoolId: '{identity_pool_id}'")
    else:
        print("\n💥 Failed to create Cognito Identity Pool")
