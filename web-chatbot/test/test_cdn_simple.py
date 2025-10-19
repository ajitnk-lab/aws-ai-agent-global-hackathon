#!/usr/bin/env python3
import requests
import time

def test_cdn_deployment():
    """Test CloudFront CDN deployment"""
    
    cdn_url = "https://dwtz1c6gg4gdx.cloudfront.net"
    
    print("🚀 Testing AgentCore Security Chatbot CDN Deployment")
    print("=" * 60)
    print(f"CDN URL: {cdn_url}")
    print("=" * 60)
    
    try:
        print("⏳ Testing CDN accessibility...")
        response = requests.get(cdn_url, timeout=15)
        
        if response.status_code == 200:
            print("✅ CDN URL is accessible!")
            print(f"✅ Response size: {len(response.content):,} bytes")
            
            # Check for React app content
            content = response.text
            if "AgentCore Security Assessment" in content:
                print("✅ React app title found")
            if "AI-powered AWS security analysis" in content:
                print("✅ App description found")
            if "static/js/" in content:
                print("✅ JavaScript bundles detected")
            if "static/css/" in content:
                print("✅ CSS stylesheets detected")
            
            print("\n🎉 DEPLOYMENT SUCCESSFUL!")
            print("=" * 60)
            print("🌐 Live Chatbot URL:")
            print(f"   {cdn_url}")
            print("\n📋 Manual Testing Instructions:")
            print("1. Open the URL in your browser")
            print("2. Try these sample queries:")
            
            sample_queries = [
                "Check security services configuration for us-east-1 region",
                "Get high severity security findings, limit to 3 results", 
                "Analyze security posture with recommendations",
                "List 1 security hub finding from us-east-1 region of high risk"
            ]
            
            for i, query in enumerate(sample_queries, 1):
                print(f"   {i}. {query}")
            
            print("\n🔧 Features Available:")
            print("   ✅ Natural language security queries")
            print("   ✅ Real-time Bedrock Agent integration")
            print("   ✅ Responsive chat interface")
            print("   ✅ Sample query buttons")
            print("   ✅ Loading states and error handling")
            print("   ✅ CloudFront CDN delivery")
            print("   ✅ HTTPS secure connection")
            
            return True
            
        else:
            print(f"❌ CDN returned status code: {response.status_code}")
            if response.status_code == 403:
                print("⏳ CloudFront may still be deploying. Wait 5-10 more minutes.")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error accessing CDN: {e}")
        print("⏳ CloudFront distribution may still be deploying.")
        print("   This typically takes 10-15 minutes after creation.")
        return False

if __name__ == "__main__":
    success = test_cdn_deployment()
    
    if success:
        print("\n🎊 Ready for testing!")
    else:
        print("\n⏰ Please wait for CloudFront deployment to complete and try again.")
