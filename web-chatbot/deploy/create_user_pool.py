#!/usr/bin/env python3
import boto3
import json

def create_user_pool():
    """Create Cognito User Pool with predefined user"""
    
    cognito_idp = boto3.client('cognito-idp', region_name='us-east-1')
    cognito_identity = boto3.client('cognito-identity', region_name='us-east-1')
    iam = boto3.client('iam', region_name='us-east-1')
    
    try:
        # Create User Pool
        user_pool = cognito_idp.create_user_pool(
            PoolName='AgentCoreSecurityChatbotUsers',
            Policies={
                'PasswordPolicy': {
                    'MinimumLength': 8,
                    'RequireUppercase': False,
                    'RequireLowercase': False,
                    'RequireNumbers': False,
                    'RequireSymbols': False
                }
            },
            AutoVerifiedAttributes=['email']
        )
        
        user_pool_id = user_pool['UserPool']['Id']
        print(f"✅ Created User Pool: {user_pool_id}")
        
        # Create User Pool Client
        client = cognito_idp.create_user_pool_client(
            UserPoolId=user_pool_id,
            ClientName='ChatbotClient',
            GenerateSecret=False,
            ExplicitAuthFlows=['ADMIN_NO_SRP_AUTH', 'ALLOW_USER_PASSWORD_AUTH', 'ALLOW_REFRESH_TOKEN_AUTH']
        )
        
        client_id = client['UserPoolClient']['ClientId']
        print(f"✅ Created User Pool Client: {client_id}")
        
        # Create predefined user
        cognito_idp.admin_create_user(
            UserPoolId=user_pool_id,
            Username='chatbot-user',
            TemporaryPassword='TempPass123!',
            MessageAction='SUPPRESS'
        )
        
        # Set permanent password
        cognito_idp.admin_set_user_password(
            UserPoolId=user_pool_id,
            Username='chatbot-user',
            Password='ChatbotPass123!',
            Permanent=True
        )
        
        print("✅ Created user: chatbot-user / ChatbotPass123!")
        
        # Update Identity Pool for authenticated users
        identity_pool_id = 'us-east-1:6feda4ed-660d-461c-8d68-90c9ce34a15a'
        
        # Create authenticated role
        auth_trust_policy = {
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
                            "cognito-identity.amazonaws.com:amr": "authenticated"
                        }
                    }
                }
            ]
        }
        
        # Create authenticated role
        auth_role = iam.create_role(
            RoleName='AgentCoreSecurityChatbot_Auth_Role',
            AssumeRolePolicyDocument=json.dumps(auth_trust_policy),
            Description='Authenticated role for Bedrock Agent access'
        )
        
        auth_role_arn = auth_role['Role']['Arn']
        print(f"✅ Created authenticated role: {auth_role_arn}")
        
        # Add Bedrock policy to authenticated role
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
            RoleName='AgentCoreSecurityChatbot_Auth_Role',
            PolicyName='BedrockAccess',
            PolicyDocument=json.dumps(policy_document)
        )
        print("✅ Added Bedrock policy to authenticated role")
        
        # Update Identity Pool with User Pool
        cognito_identity.update_identity_pool(
            IdentityPoolId=identity_pool_id,
            IdentityPoolName='AgentCoreSecurityChatbotFixed',
            AllowUnauthenticatedIdentities=False,
            CognitoIdentityProviders=[
                {
                    'ProviderName': f'cognito-idp.us-east-1.amazonaws.com/{user_pool_id}',
                    'ClientId': client_id
                }
            ]
        )
        print("✅ Updated Identity Pool with User Pool")
        
        # Set roles for authenticated users
        cognito_identity.set_identity_pool_roles(
            IdentityPoolId=identity_pool_id,
            Roles={
                'authenticated': auth_role_arn
            }
        )
        print("✅ Set authenticated role")
        
        return user_pool_id, client_id, identity_pool_id
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None, None

if __name__ == "__main__":
    user_pool_id, client_id, identity_pool_id = create_user_pool()
    if user_pool_id:
        print(f"\n🎉 Cognito User Pool created successfully!")
        print(f"User Pool ID: {user_pool_id}")
        print(f"Client ID: {client_id}")
        print(f"Identity Pool ID: {identity_pool_id}")
        print(f"\n👤 Predefined User:")
        print(f"Username: chatbot-user")
        print(f"Password: ChatbotPass123!")
        print(f"\n🔧 Update your React app with these values")
    else:
        print("\n💥 Failed to create User Pool")
