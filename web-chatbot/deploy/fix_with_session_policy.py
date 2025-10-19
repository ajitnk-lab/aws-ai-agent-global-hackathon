#!/usr/bin/env python3
import boto3
import json

def fix_with_session_policy():
    """Fix by embedding session policy in trust relationship"""
    
    iam = boto3.client('iam', region_name='us-east-1')
    cognito_identity = boto3.client('cognito-identity', region_name='us-east-1')
    
    pool_id = 'us-east-1:6feda4ed-660d-461c-8d68-90c9ce34a15a'
    role_name = 'AgentCoreSecurityChatbot_Fixed_Role'
    
    try:
        # Create trust policy with embedded session policy
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
                            "cognito-identity.amazonaws.com:aud": pool_id
                        },
                        "ForAnyValue:StringLike": {
                            "cognito-identity.amazonaws.com:amr": "unauthenticated"
                        }
                    }
                }
            ]
        }
        
        # Update trust policy
        iam.update_assume_role_policy(
            RoleName=role_name,
            PolicyDocument=json.dumps(trust_policy)
        )
        print("✅ Updated trust policy")
        
        # Set identity pool roles with session policy
        cognito_identity.set_identity_pool_roles(
            IdentityPoolId=pool_id,
            Roles={
                'unauthenticated': f'arn:aws:iam::039920874011:role/{role_name}'
            },
            RoleMappings={
                'cognito-identity.amazonaws.com': {
                    'Type': 'Rules',
                    'AmbiguousRoleResolution': 'AuthenticatedRole',
                    'RulesConfiguration': {
                        'Rules': [
                            {
                                'Claim': 'cognito:preferred_role',
                                'MatchType': 'Equals',
                                'Value': 'unauthenticated',
                                'RoleARN': f'arn:aws:iam::039920874011:role/{role_name}'
                            }
                        ]
                    }
                }
            }
        )
        print("✅ Updated identity pool with role mappings")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    if fix_with_session_policy():
        print("\n🎉 Applied session policy fix!")
        print("⏳ Wait 2-3 minutes and test again")
    else:
        print("\n💥 Session policy fix failed")
