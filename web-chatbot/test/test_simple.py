#!/usr/bin/env python3
import requests
import time

def test_chatbot_manually():
    """Instructions for manual testing"""
    
    print("🧪 Manual Testing Instructions")
    print("=" * 50)
    print("1. Open: https://dwtz1c6gg4gdx.cloudfront.net")
    print("2. Try this query: 'Hello, can you help me?'")
    print("3. If you get an authorization error, the IAM policy needs more time")
    print("4. If it works, try: 'Check security services for us-east-1'")
    print("\n✅ IAM Policy has been updated with broader permissions")
    print("⏳ Allow 5-10 minutes for full propagation across AWS")
    
    print("\n🔧 What was fixed:")
    print("   • Added bedrock:InvokeAgent permission")
    print("   • Added bedrock:Retrieve permission") 
    print("   • Added bedrock:RetrieveAndGenerate permission")
    print("   • Used wildcard (*) resource for maximum compatibility")
    
    print("\n🌐 Live URL: https://dwtz1c6gg4gdx.cloudfront.net")

if __name__ == "__main__":
    test_chatbot_manually()
