#!/usr/bin/env python3
import boto3

def optimize_cloudfront_caching():
    """Optimize CloudFront caching for static assets"""
    
    cloudfront = boto3.client('cloudfront', region_name='us-east-1')
    distribution_id = 'EPF5G78R8F38H'
    
    try:
        # Get current distribution config
        response = cloudfront.get_distribution_config(Id=distribution_id)
        config = response['DistributionConfig']
        etag = response['ETag']
        
        # Add cache behaviors for different file types
        cache_behaviors = [
            {
                'PathPattern': '*.js',
                'TargetOriginId': config['Origins']['Items'][0]['Id'],
                'ViewerProtocolPolicy': 'redirect-to-https',
                'TrustedSigners': {'Enabled': False, 'Quantity': 0},
                'ForwardedValues': {'QueryString': False, 'Cookies': {'Forward': 'none'}},
                'MinTTL': 0,
                'DefaultTTL': 31536000,  # 1 year for JS files
                'MaxTTL': 31536000,
                'Compress': True
            },
            {
                'PathPattern': '*.css',
                'TargetOriginId': config['Origins']['Items'][0]['Id'],
                'ViewerProtocolPolicy': 'redirect-to-https',
                'TrustedSigners': {'Enabled': False, 'Quantity': 0},
                'ForwardedValues': {'QueryString': False, 'Cookies': {'Forward': 'none'}},
                'MinTTL': 0,
                'DefaultTTL': 31536000,  # 1 year for CSS files
                'MaxTTL': 31536000,
                'Compress': True
            },
            {
                'PathPattern': '*.html',
                'TargetOriginId': config['Origins']['Items'][0]['Id'],
                'ViewerProtocolPolicy': 'redirect-to-https',
                'TrustedSigners': {'Enabled': False, 'Quantity': 0},
                'ForwardedValues': {'QueryString': False, 'Cookies': {'Forward': 'none'}},
                'MinTTL': 0,
                'DefaultTTL': 300,  # 5 minutes for HTML files
                'MaxTTL': 86400,
                'Compress': True
            }
        ]
        
        # Update cache behaviors
        if 'CacheBehaviors' not in config:
            config['CacheBehaviors'] = {'Quantity': 0, 'Items': []}
        
        config['CacheBehaviors']['Items'].extend(cache_behaviors)
        config['CacheBehaviors']['Quantity'] = len(config['CacheBehaviors']['Items'])
        
        # Update distribution
        cloudfront.update_distribution(
            Id=distribution_id,
            DistributionConfig=config,
            IfMatch=etag
        )
        
        print("✅ CloudFront caching optimized!")
        print("📈 Cache settings:")
        print("   • JavaScript files: 1 year cache")
        print("   • CSS files: 1 year cache") 
        print("   • HTML files: 5 minutes cache")
        print("   • Compression enabled for all files")
        
        return True
        
    except Exception as e:
        print(f"❌ Error optimizing CloudFront: {e}")
        return False

if __name__ == "__main__":
    if optimize_cloudfront_caching():
        print("\n🎉 CloudFront optimization complete!")
        print("⏳ Changes will take 10-15 minutes to deploy globally.")
    else:
        print("\n💥 CloudFront optimization failed!")
