#!/usr/bin/env python3
import boto3
import os
import mimetypes
from pathlib import Path

def deploy_to_s3():
    """Deploy React build to S3 bucket"""
    
    s3 = boto3.client('s3', region_name='us-east-1')
    bucket_name = 'agentcore-security-chatbot-370c5066'
    build_dir = Path('../build')
    
    if not build_dir.exists():
        print("❌ Build directory not found. Run 'npm run build' first.")
        return False
    
    try:
        # Upload all files from build directory
        for file_path in build_dir.rglob('*'):
            if file_path.is_file():
                # Get relative path for S3 key
                s3_key = str(file_path.relative_to(build_dir)).replace('\\', '/')
                
                # Determine content type
                content_type, _ = mimetypes.guess_type(str(file_path))
                if content_type is None:
                    content_type = 'binary/octet-stream'
                
                # Upload file
                with open(file_path, 'rb') as f:
                    s3.put_object(
                        Bucket=bucket_name,
                        Key=s3_key,
                        Body=f.read(),
                        ContentType=content_type
                    )
                
                print(f"✅ Uploaded: {s3_key}")
        
        print(f"\n🎉 Successfully deployed to S3!")
        print(f"S3 Website URL: http://{bucket_name}.s3-website-us-east-1.amazonaws.com")
        print(f"CloudFront URL: https://dwtz1c6gg4gdx.cloudfront.net")
        
        return True
        
    except Exception as e:
        print(f"❌ Error deploying to S3: {e}")
        return False

if __name__ == "__main__":
    deploy_to_s3()
