"""
Complete deployment script for AgentCore Security Assessment Application
"""
import subprocess
import sys
import os
import json
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return None

def deploy_memory():
    """Deploy AgentCore Memory"""
    print("\n" + "="*60)
    print("STEP 1: Deploying AgentCore Memory")
    print("="*60)
    
    os.chdir("../memory")
    output = run_command("python setup_memory.py", "Memory deployment")
    
    if output and "Memory ID:" in output:
        # Extract memory ID from output
        for line in output.split('\n'):
            if "Memory ID:" in line:
                memory_id = line.split("Memory ID:")[-1].strip()
                os.environ['BEDROCK_AGENTCORE_MEMORY_ID'] = memory_id
                print(f"📝 Memory ID set: {memory_id}")
                break
    
    return output is not None

def deploy_runtime():
    """Deploy AgentCore Runtime"""
    print("\n" + "="*60)
    print("STEP 2: Deploying AgentCore Runtime")
    print("="*60)
    
    os.chdir("../runtime")
    
    # Configure runtime
    configure_output = run_command(
        "agentcore configure -e security_agent.py",
        "Runtime configuration"
    )
    
    if not configure_output:
        return False
    
    # Launch runtime
    launch_output = run_command(
        "agentcore launch",
        "Runtime deployment"
    )
    
    if launch_output and "Agent ARN:" in launch_output:
        # Extract runtime ARN
        for line in launch_output.split('\n'):
            if "Agent ARN:" in line:
                runtime_arn = line.split("Agent ARN:")[-1].strip()
                os.environ['AGENTCORE_RUNTIME_ARN'] = runtime_arn
                print(f"📝 Runtime ARN set: {runtime_arn}")
                break
    
    return launch_output is not None

def deploy_gateway():
    """Deploy AgentCore Gateway"""
    print("\n" + "="*60)
    print("STEP 3: Deploying AgentCore Gateway")
    print("="*60)
    
    os.chdir("../gateway")
    output = run_command("python setup_gateway.py", "Gateway deployment")
    return output is not None

def deploy_bedrock_agent():
    """Deploy Bedrock Agent"""
    print("\n" + "="*60)
    print("STEP 4: Deploying Bedrock Agent")
    print("="*60)
    
    os.chdir("../bedrock")
    
    # Deploy Lambda bridge function
    lambda_output = run_command(
        "python deploy_lambda_bridge.py",
        "Lambda bridge deployment"
    )
    
    if not lambda_output:
        return False
    
    # Deploy Bedrock Agent
    agent_output = run_command(
        "python deploy_bedrock_agent.py", 
        "Bedrock Agent deployment"
    )
    
    return agent_output is not None

def main():
    """Main deployment orchestration"""
    print("🚀 Starting AgentCore Security Assessment Application Deployment")
    print("This will deploy: Memory → Runtime → Gateway → Bedrock Agent")
    
    # Check prerequisites
    if not os.getenv('AWS_REGION'):
        print("❌ AWS_REGION environment variable required")
        sys.exit(1)
    
    # Store original directory
    original_dir = os.getcwd()
    
    try:
        # Step 1: Deploy Memory
        if not deploy_memory():
            print("❌ Memory deployment failed")
            sys.exit(1)
        
        # Step 2: Deploy Runtime
        if not deploy_runtime():
            print("❌ Runtime deployment failed")
            sys.exit(1)
        
        # Step 3: Deploy Gateway
        if not deploy_gateway():
            print("❌ Gateway deployment failed")
            sys.exit(1)
        
        # Step 4: Deploy Bedrock Agent
        if not deploy_bedrock_agent():
            print("❌ Bedrock Agent deployment failed")
            sys.exit(1)
        
        print("\n" + "="*60)
        print("🎉 DEPLOYMENT COMPLETE!")
        print("="*60)
        print("✅ AgentCore Memory: Deployed")
        print("✅ AgentCore Runtime: Deployed")
        print("✅ AgentCore Gateway: Deployed with OAuth")
        print("✅ Bedrock Agent: Deployed with Lambda bridge")
        
        print(f"\n📋 Environment Variables:")
        print(f"   BEDROCK_AGENTCORE_MEMORY_ID: {os.getenv('BEDROCK_AGENTCORE_MEMORY_ID', 'Not set')}")
        print(f"   AGENTCORE_RUNTIME_ARN: {os.getenv('AGENTCORE_RUNTIME_ARN', 'Not set')}")
        
        print(f"\n🧪 Test your deployment:")
        print(f"   cd ../test && python test_integration.py")
        
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")
        sys.exit(1)
    finally:
        os.chdir(original_dir)

if __name__ == "__main__":
    main()
