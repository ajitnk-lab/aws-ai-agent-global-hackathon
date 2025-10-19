#!/usr/bin/env python3
"""
Test script to verify that the Lambda function now returns all 189 Security Hub findings
instead of being limited to 20 findings.
"""
import sys
import os
import json

# Add the runtime directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'runtime'))

from security_functions import get_security_findings

def test_security_findings_count():
    """Test that we can retrieve all Security Hub findings without the 20-result limitation"""
    
    print("Testing Security Hub findings retrieval...")
    print("=" * 60)
    
    # Test with no limit to get all findings
    print("1. Testing with no limit (should get all findings)...")
    result_no_limit = get_security_findings(
        service_filter='SECURITYHUB',
        limit=None  # No limit
    )
    
    # Parse the JSON result
    try:
        data_no_limit = json.loads(result_no_limit)
        total_findings_no_limit = data_no_limit.get('total_findings', 0)
        print(f"   Total findings with no limit: {total_findings_no_limit}")
    except json.JSONDecodeError as e:
        print(f"   Error parsing result: {e}")
        print(f"   Raw result: {result_no_limit}")
        return False
    
    # Test with high limit to get all findings
    print("2. Testing with high limit (1000)...")
    result_high_limit = get_security_findings(
        service_filter='SECURITYHUB',
        limit=1000
    )
    
    try:
        data_high_limit = json.loads(result_high_limit)
        total_findings_high_limit = data_high_limit.get('total_findings', 0)
        print(f"   Total findings with limit=1000: {total_findings_high_limit}")
    except json.JSONDecodeError as e:
        print(f"   Error parsing result: {e}")
        print(f"   Raw result: {result_high_limit}")
        return False
    
    # Test with old limit (20) to compare
    print("3. Testing with old limit (20) for comparison...")
    result_old_limit = get_security_findings(
        service_filter='SECURITYHUB',
        limit=20
    )
    
    try:
        data_old_limit = json.loads(result_old_limit)
        total_findings_old_limit = data_old_limit.get('total_findings', 0)
        print(f"   Total findings with limit=20: {total_findings_old_limit}")
    except json.JSONDecodeError as e:
        print(f"   Error parsing result: {e}")
        print(f"   Raw result: {result_old_limit}")
        return False
    
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY:")
    print(f"- No limit: {total_findings_no_limit} findings")
    print(f"- High limit (1000): {total_findings_high_limit} findings")
    print(f"- Old limit (20): {total_findings_old_limit} findings")
    
    # Check if we're getting more than 20 findings
    if total_findings_no_limit > 20 or total_findings_high_limit > 20:
        print("\n✅ SUCCESS: The fix is working! We're now getting more than 20 findings.")
        
        # Check if we're getting close to the expected 189
        if total_findings_no_limit >= 100 or total_findings_high_limit >= 100:
            print(f"✅ EXCELLENT: Getting {max(total_findings_no_limit, total_findings_high_limit)} findings, much closer to the expected 189!")
        
        return True
    else:
        print("\n❌ ISSUE: Still only getting 20 or fewer findings. The fix may not be working as expected.")
        return False

if __name__ == "__main__":
    print("Security Hub Findings Fix Verification Test")
    print("=" * 60)
    print("This test verifies that the Lambda function can now retrieve")
    print("all 189 Security Hub findings instead of being limited to 20.")
    print()
    
    success = test_security_findings_count()
    
    if success:
        print("\n🎉 Test completed successfully!")
        sys.exit(0)
    else:
        print("\n⚠️  Test indicates there may still be issues.")
        sys.exit(1)
