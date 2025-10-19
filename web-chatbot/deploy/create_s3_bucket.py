#!/usr/bin/env python3
import boto3
import json
import uuid

def create_s3_bucket():
    """Create S3 bucket for static website hosting"""
    
    s3_client = boto3.client('s3', region_name='us-east-1')
    
    # Generate unique bucket name
    bucket_name = f"agentcore-security-chatbot-{str(uuid.uuid4())[:8]}"
    
    try:
        # Create S3 bucket
        s3_client.create_bucket(Bucket=bucket_name)
        print(f"✅ Created S3 bucket: {bucket_name}")
        
        # Enable static website hosting
        s3_client.put_bucket_website(
            Bucket=bucket_name,
            WebsiteConfiguration={
                'IndexDocument': {'Suffix': 'index.html'},
                'ErrorDocument': {'Key': 'error.html'}
            }
        )
        print("✅ Enabled static website hosting")
        
        # Block public access initially (will be accessed via CloudFront)
        s3_client.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
        )
        print("✅ Configured public access block")
        
        return bucket_name
        
    except Exception as e:
        print(f"❌ Error creating S3 bucket: {e}")
        return None

if __name__ == "__main__":
    bucket_name = create_s3_bucket()
    if bucket_name:
        print(f"\n🎉 S3 bucket created successfully!")
        print(f"Bucket name: {bucket_name}")
        print(f"Website endpoint: http://{bucket_name}.s3-website-us-east-1.amazonaws.com")
    else:
        print("\n💥 Failed to create S3 bucket")
