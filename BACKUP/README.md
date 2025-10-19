# AgentCore Security Assessment Application

A complete transformation of the AWS Well-Architected Security MCP server into a production-ready AgentCore application with:

- **AgentCore Runtime**: Secure agent execution environment with security tools
- **AgentCore Gateway**: OAuth-protected API gateway for security assessments  
- **AgentCore Memory**: Persistent security context and findings storage
- **Bedrock Agent Integration**: Native AWS Bedrock Agent orchestration

## Architecture

```
User Request 
    ↓
Bedrock Agent (orchestrates security assessments)
    ↓
Lambda Bridge Function (handles OAuth)
    ↓
AgentCore Gateway (OAuth protected security tools)
    ↓
AgentCore Runtime (security assessment agent)
    ↓
AgentCore Memory (persistent security context)
```

## Prerequisites

- AWS CLI configured with appropriate permissions
- Python 3.10 or newer
- AgentCore CLI installed (`pip install bedrock-agentcore-starter-toolkit`)
- Access to Amazon Bedrock models (Claude 3.7 Sonnet)

## Quick Start

### 1. Install Dependencies

```bash
cd agentcore-security-app
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
export AWS_REGION=us-east-1  # Your preferred region
export AWS_PROFILE=default   # Your AWS profile
```

### 3. Deploy All Components (Automated)

```bash
cd deploy
python deploy_all.py
```

This will automatically deploy:
1. AgentCore Memory with security-focused strategies
2. AgentCore Runtime with security assessment tools
3. AgentCore Gateway with OAuth integration
4. Lambda bridge function for Bedrock Agent communication
5. Bedrock Agent with comprehensive security action groups

### 4. Test the Integration

```bash
cd ../test
python test_integration.py
```

## Manual Deployment (Step by Step)

If you prefer manual control over the deployment:

### Step 1: Deploy Memory

```bash
cd memory
python setup_memory.py
# Note the Memory ID and set environment variable
export BEDROCK_AGENTCORE_MEMORY_ID=<memory-id>
```

### Step 2: Deploy Runtime

```bash
cd ../runtime
agentcore configure -e security_agent.py
agentcore launch
# Note the Runtime ARN
export AGENTCORE_RUNTIME_ARN=<runtime-arn>
```

### Step 3: Deploy Gateway

```bash
cd ../gateway
python setup_gateway.py
```

### Step 4: Deploy Bedrock Agent

```bash
cd ../bedrock
python deploy_lambda_bridge.py
python deploy_bedrock_agent.py
```

## Security Tools Available

The application provides comprehensive AWS security assessment capabilities:

### 🔍 **CheckSecurityServices**
- Monitor operational status of GuardDuty, Security Hub, Inspector, IAM Access Analyzer
- Identify service availability across regions
- Provide recommendations for maintaining security service coverage

### 🚨 **GetSecurityFindings**
- Collect security findings from Security Hub, GuardDuty, and Inspector
- Filter findings by severity (LOW, MEDIUM, HIGH, CRITICAL)
- Provide actionable remediation guidance

### 📊 **AnalyzeSecurityPosture**
- Comprehensive security assessment against AWS Well-Architected Framework
- Evaluate Identity & Access Management, Detective Controls, Infrastructure Protection
- Generate security scores and prioritized recommendations

### 🔎 **ExploreAwsResources**
- Discover resources across AWS services (EC2, S3, RDS, Lambda, IAM)
- Map resource relationships for security context
- Identify resources requiring security attention

### ✅ **GetResourceComplianceStatus**
- Check compliance against security standards
- Identify non-compliant resources
- Provide compliance metrics and improvement recommendations

## Usage Examples

### Direct Bedrock Agent Interaction

```python
import boto3

bedrock_runtime = boto3.client('bedrock-agent-runtime')

response = bedrock_runtime.invoke_agent(
    agentId='your-agent-id',
    agentAliasId='TSTALIASID',
    sessionId='security-assessment-session',
    inputText="Perform a comprehensive security assessment of my AWS account"
)
```

### Gateway Direct Access (with OAuth)

```python
import httpx
import asyncio

async def call_security_tool():
    # Get OAuth token
    token_response = await httpx.AsyncClient().post(
        'your-cognito-token-endpoint',
        data={
            'grant_type': 'client_credentials',
            'client_id': 'your-client-id',
            'client_secret': 'your-client-secret',
            'scope': 'your-scope'
        }
    )
    
    token = token_response.json()['access_token']
    
    # Call security tool
    response = await httpx.AsyncClient().post(
        'your-gateway-url',
        headers={'Authorization': f'Bearer {token}'},
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "analyze_security_posture",
                "arguments": {}
            }
        }
    )
    
    return response.json()
```

## Project Structure

```
agentcore-security-app/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── runtime/                     # AgentCore Runtime
│   ├── security_agent.py       # Main agent with security tools
│   ├── security_tools.py       # Core security assessment logic
│   └── requirements.txt        # Runtime-specific dependencies
├── memory/                      # AgentCore Memory
│   └── setup_memory.py         # Memory configuration script
├── gateway/                     # AgentCore Gateway
│   └── setup_gateway.py        # Gateway with OAuth setup
├── bedrock/                     # Bedrock Agent Integration
│   ├── deploy_bedrock_agent.py # Bedrock Agent deployment
│   ├── lambda_bridge.py        # Lambda bridge function
│   └── deploy_lambda_bridge.py # Lambda deployment script
├── deploy/                      # Deployment Scripts
│   └── deploy_all.py           # Automated deployment
└── test/                        # Integration Tests
    └── test_integration.py     # End-to-end testing
```

## Configuration Files

After deployment, you'll find these configuration files:

- `memory/.env` - Memory ID and region settings
- `gateway/gateway_config.json` - Gateway URL and OAuth credentials
- `bedrock/lambda_bridge_config.json` - Lambda function details
- `bedrock/bedrock_agent_config.json` - Bedrock Agent configuration

## Troubleshooting

### Common Issues

1. **Memory not found**: Ensure `BEDROCK_AGENTCORE_MEMORY_ID` is set correctly
2. **Gateway OAuth errors**: Check Cognito client credentials in configuration
3. **Lambda timeout**: Increase Lambda timeout if security assessments take longer
4. **Bedrock Agent permissions**: Ensure IAM roles have necessary permissions

### Debug Commands

```bash
# Check AgentCore Runtime status
agentcore status

# Test Gateway directly
cd test && python -c "import asyncio; asyncio.run(test_gateway_direct())"

# Check Lambda logs
aws logs tail /aws/lambda/your-lambda-function-name --follow
```

## Security Considerations

- **IAM Permissions**: Use least-privilege IAM roles for all components
- **OAuth Tokens**: Tokens are cached and automatically refreshed
- **Memory Encryption**: AgentCore Memory encrypts data at rest
- **Network Security**: Gateway uses HTTPS with OAuth 2.0 protection

## Cost Optimization

- **Memory Retention**: Security context retained for 90 days (configurable)
- **Lambda Concurrency**: Bridge function uses minimal resources
- **Runtime Scaling**: AgentCore Runtime scales automatically based on demand
- **API Calls**: Security tools are optimized to minimize AWS API calls

## Support

For issues and questions:
1. Check the integration tests: `python test/test_integration.py`
2. Review AWS CloudWatch logs for detailed error information
3. Ensure all environment variables are properly configured
4. Verify AWS permissions for all services

## License

This project is licensed under the Apache License, Version 2.0 - same as the original AWS Well-Architected Security MCP Server.
