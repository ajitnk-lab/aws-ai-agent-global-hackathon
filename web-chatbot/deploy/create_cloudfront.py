#!/usr/bin/env python3
import boto3
import json
import time

def create_cloudfront_distribution():
    """Create CloudFront distribution with OAC for S3 bucket"""
    
    cloudfront = boto3.client('cloudfront', region_name='us-east-1')
    s3 = boto3.client('s3', region_name='us-east-1')
    
    bucket_name = 'agentcore-security-chatbot-370c5066'
    
    try:
        # Create Origin Access Control (OAC)
        oac_response = cloudfront.create_origin_access_control(
            OriginAccessControlConfig={
                'Name': f'{bucket_name}-oac',
                'Description': 'OAC for AgentCore Security Chatbot',
                'OriginAccessControlOriginType': 's3',
                'SigningBehavior': 'always',
                'SigningProtocol': 'sigv4'
            }
        )
        
        oac_id = oac_response['OriginAccessControl']['Id']
        print(f"✅ Created OAC: {oac_id}")
        
        # Create CloudFront distribution
        distribution_config = {
            'CallerReference': f'agentcore-chatbot-{int(time.time())}',
            'Comment': 'AgentCore Security Assessment Chatbot',
            'DefaultRootObject': 'index.html',
            'Origins': {
                'Quantity': 1,
                'Items': [
                    {
                        'Id': f'{bucket_name}-origin',
                        'DomainName': f'{bucket_name}.s3.us-east-1.amazonaws.com',
                        'S3OriginConfig': {
                            'OriginAccessIdentity': ''
                        },
                        'OriginAccessControlId': oac_id
                    }
                ]
            },
            'DefaultCacheBehavior': {
                'TargetOriginId': f'{bucket_name}-origin',
                'ViewerProtocolPolicy': 'redirect-to-https',
                'TrustedSigners': {
                    'Enabled': False,
                    'Quantity': 0
                },
                'ForwardedValues': {
                    'QueryString': False,
                    'Cookies': {'Forward': 'none'}
                },
                'MinTTL': 0,
                'DefaultTTL': 86400,
                'MaxTTL': 31536000,
                'Compress': True
            },
            'Enabled': True,
            'PriceClass': 'PriceClass_100'
        }
        
        distribution_response = cloudfront.create_distribution(
            DistributionConfig=distribution_config
        )
        
        distribution_id = distribution_response['Distribution']['Id']
        domain_name = distribution_response['Distribution']['DomainName']
        
        print(f"✅ Created CloudFront distribution: {distribution_id}")
        print(f"✅ Domain name: {domain_name}")
        
        # Update S3 bucket policy for OAC
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AllowCloudFrontServicePrincipal",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "cloudfront.amazonaws.com"
                    },
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/*",
                    "Condition": {
                        "StringEquals": {
                            "AWS:SourceArn": f"arn:aws:cloudfront::039920874011:distribution/{distribution_id}"
                        }
                    }
                }
            ]
        }
        
        s3.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(bucket_policy)
        )
        print("✅ Updated S3 bucket policy for OAC")
        
        return distribution_id, domain_name
        
    except Exception as e:
        print(f"❌ Error creating CloudFront distribution: {e}")
        return None, None

if __name__ == "__main__":
    distribution_id, domain_name = create_cloudfront_distribution()
    if distribution_id:
        print(f"\n🎉 CloudFront distribution created successfully!")
        print(f"Distribution ID: {distribution_id}")
        print(f"Domain name: {domain_name}")
        print(f"CDN URL: https://{domain_name}")
        print(f"\n⏳ Distribution is deploying... This may take 10-15 minutes.")
    else:
        print("\n💥 Failed to create CloudFront distribution")
