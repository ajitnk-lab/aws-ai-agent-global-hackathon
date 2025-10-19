#!/usr/bin/env python3
import subprocess
import json
import os

def deploy_gateway():
    """Deploy AgentCore Gateway using CLI commands"""
    
    # Create MCP Gateway
    print("Creating MCP Gateway...")
    result = subprocess.run([
        "agentcore", "gateway", "create-mcp-gateway",
        "--name", "security-gateway",
        "--region", "us-east-1"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Gateway creation failed: {result.stderr}")
        return False
    
    print("Gateway created successfully!")
    print(result.stdout)
    
    return True

if __name__ == "__main__":
    success = deploy_gateway()
    if success:
        print("\n✅ Gateway deployment completed successfully!")
    else:
        print("\n❌ Gateway deployment failed!")
