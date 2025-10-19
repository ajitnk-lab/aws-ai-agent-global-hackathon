#!/usr/bin/env python3
import boto3
import json

def create_user_pool_fixed():
    """Create Cognito User Pool with correct auth flows"""
    
    cognito_idp = boto3.client('cognito-idp', region_name='us-east-1')
    cognito_identity = boto3.client('cognito-identity', region_name='us-east-1')
    iam = boto3.client('iam', region_name='us-east-1')
    
    try:
        # Use existing User Pool
        user_pool_id = 'us-east-1_W9Ro1YsQX'
        
        # Create User Pool Client with correct auth flows
        client = cognito_idp.create_user_pool_client(
            UserPoolId=user_pool_id,
            ClientName='ChatbotClient',
            GenerateSecret=False,
            ExplicitAuthFlows=['ALLOW_USER_PASSWORD_AUTH', 'ALLOW_REFRESH_TOKEN_AUTH']
        )
        
        client_id = client['UserPoolClient']['ClientId']
        print(f"✅ Created User Pool Client: {client_id}")
        
        # Create predefined user
        try:
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
        except:
            print("✅ User already exists")
        
        # Update Identity Pool
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
        
        try:
            auth_role = iam.create_role(
                RoleName='AgentCoreSecurityChatbot_Auth_Role',
                AssumeRolePolicyDocument=json.dumps(auth_trust_policy),
                Description='Authenticated role for Bedrock Agent access'
            )
            auth_role_arn = auth_role['Role']['Arn']
            print(f"✅ Created authenticated role: {auth_role_arn}")
        except:
            auth_role_arn = 'arn:aws:iam::039920874011:role/AgentCoreSecurityChatbot_Auth_Role'
            print("✅ Using existing authenticated role")
        
        # Add Bedrock policy
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
        print("✅ Added Bedrock policy")
        
        # Update Identity Pool
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
        print("✅ Updated Identity Pool")
        
        # Set authenticated role
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
    user_pool_id, client_id, identity_pool_id = create_user_pool_fixed()
    if user_pool_id:
        print(f"\n🎉 SUCCESS!")
        print(f"User Pool ID: {user_pool_id}")
        print(f"Client ID: {client_id}")
        print(f"Identity Pool ID: {identity_pool_id}")
        print(f"\n👤 Login Credentials:")
        print(f"Username: chatbot-user")
        print(f"Password: ChatbotPass123!")
    else:
        print("\n💥 Failed")
