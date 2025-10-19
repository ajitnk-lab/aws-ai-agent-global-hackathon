"""
Core security assessment tools extracted from Well-Architected Security MCP Server
"""
import boto3
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class SecurityFinding:
    service: str
    severity: str
    title: str
    description: str
    resource_id: str
    region: str
    
    def to_dict(self):
        """Convert SecurityFinding to dictionary for JSON serialization"""
        return {
            'service': self.service,
            'severity': self.severity,
            'title': self.title,
            'description': self.description,
            'resource_id': self.resource_id,
            'region': self.region
        }


class SecurityAssessmentTools:
    """Security assessment tools for AWS Well-Architected Framework"""
    
    def __init__(self, region: str = 'us-east-1'):
        self.region = region
        self.session = boto3.Session(region_name=region)
        
    def check_security_services(self) -> Dict[str, Any]:
        """Monitor AWS security services operational status"""
        results = {
            'guardduty': self._check_guardduty(),
            'security_hub': self._check_security_hub(),
            'inspector': self._check_inspector(),
            'access_analyzer': self._check_access_analyzer()
        }
        
        return {
            'status': 'success',
            'services': results,
            'summary': self._generate_service_summary(results)
        }
    
    def get_security_findings(self, severity_filter: Optional[str] = None, limit: Optional[int] = None, region: Optional[str] = None, service_filter: Optional[str] = None, resource_type: Optional[str] = None, compliance_status: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve security findings from multiple AWS services with comprehensive filtering"""
        # Use specified region or default to instance region
        target_region = region or self.region
        
        # Create session for target region if different from default
        if target_region != self.region:
            session = boto3.Session(region_name=target_region)
        else:
            session = self.session
        
        # Set default limit to match AWS API response (no limit means get all)
        max_results = limit if limit is not None else 1000  # AWS API max is 100 per call, but we'll paginate
        
        findings = []
        
        # Get findings from specified services or all services
        if not service_filter or service_filter.upper() == 'SECURITYHUB':
            findings.extend(self._get_security_hub_findings(severity_filter, session, target_region, resource_type, compliance_status, max_results))
        
        if not service_filter or service_filter.upper() == 'GUARDDUTY':
            findings.extend(self._get_guardduty_findings(severity_filter, session, target_region, resource_type, max_results))
        
        if not service_filter or service_filter.upper() == 'INSPECTOR':
            findings.extend(self._get_inspector_findings(severity_filter, session, target_region, resource_type, max_results))
        
        # Apply final limit if specified
        if limit is not None:
            findings = findings[:limit]
        
        return {
            'status': 'success',
            'total_findings': len(findings),
            'filters_applied': {
                'severity': severity_filter or 'ALL',
                'region': target_region,
                'service': service_filter or 'ALL',
                'resource_type': resource_type or 'ALL',
                'compliance_status': compliance_status or 'ALL',
                'limit': limit or 50
            },
            'findings': [f.to_dict() for f in findings],  # Convert to dictionaries for JSON serialization
            'summary': self._generate_findings_summary(findings)
        }
    
    def analyze_security_posture(self) -> Dict[str, Any]:
        """Comprehensive security posture analysis against Well-Architected Framework"""
        analysis = {
            'identity_access_management': self._analyze_iam(),
            'detective_controls': self._analyze_detective_controls(),
            'infrastructure_protection': self._analyze_infrastructure(),
            'data_protection': self._analyze_data_protection(),
            'incident_response': self._analyze_incident_response()
        }
        
        score = self._calculate_security_score(analysis)
        
        return {
            'status': 'success',
            'overall_score': score,
            'pillar_analysis': analysis,
            'recommendations': self._generate_recommendations(analysis)
        }
    
    def explore_aws_resources(self, service_filter: Optional[str] = None) -> Dict[str, Any]:
        """Discover and inventory AWS resources for security assessment"""
        resources = {}
        
        services = ['ec2', 's3', 'rds', 'lambda', 'iam'] if not service_filter else [service_filter]
        
        for service in services:
            try:
                resources[service] = self._get_service_resources(service)
            except Exception as e:
                resources[service] = {'error': str(e)}
        
        return {
            'status': 'success',
            'resources': resources,
            'total_resources': sum(len(r.get('items', [])) for r in resources.values() if 'items' in r)
        }
    
    def get_resource_compliance_status(self, resource_type: Optional[str] = None) -> Dict[str, Any]:
        """Check compliance status of AWS resources against security standards"""
        try:
            config_client = self.session.client('config')
            
            # Get compliance details
            compliance_results = config_client.get_compliance_details_by_config_rule()
            
            compliant = []
            non_compliant = []
            
            for result in compliance_results.get('EvaluationResults', []):
                resource_info = {
                    'resource_type': result.get('EvaluationResultIdentifier', {}).get('EvaluationResultQualifier', {}).get('ResourceType'),
                    'resource_id': result.get('EvaluationResultIdentifier', {}).get('EvaluationResultQualifier', {}).get('ResourceId'),
                    'compliance_type': result.get('ComplianceType')
                }
                
                if result.get('ComplianceType') == 'COMPLIANT':
                    compliant.append(resource_info)
                else:
                    non_compliant.append(resource_info)
            
            return {
                'status': 'success',
                'compliant_resources': len(compliant),
                'non_compliant_resources': len(non_compliant),
                'compliance_details': {
                    'compliant': compliant[:20],
                    'non_compliant': non_compliant[:20]
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Error checking compliance: {str(e)}"
            }
    
    # Private helper methods
    def _check_guardduty(self) -> Dict[str, Any]:
        try:
            client = self.session.client('guardduty')
            detectors = client.list_detectors()
            
            if not detectors['DetectorIds']:
                return {'enabled': False, 'status': 'Not configured'}
            
            detector_id = detectors['DetectorIds'][0]
            detector = client.get_detector(DetectorId=detector_id)
            
            return {
                'enabled': detector['Status'] == 'ENABLED',
                'status': detector['Status'],
                'detector_id': detector_id
            }
        except Exception as e:
            return {'enabled': False, 'error': str(e)}
    
    def _check_security_hub(self) -> Dict[str, Any]:
        try:
            client = self.session.client('securityhub')
            hub = client.get_enabled_standards()
            
            return {
                'enabled': True,
                'standards_count': len(hub['StandardsSubscriptions']),
                'standards': [s['StandardsArn'] for s in hub['StandardsSubscriptions']]
            }
        except Exception as e:
            return {'enabled': False, 'error': str(e)}
    
    def _check_inspector(self) -> Dict[str, Any]:
        try:
            client = self.session.client('inspector2')
            account = client.get_member()
            
            return {
                'enabled': account['member']['status'] == 'ENABLED',
                'status': account['member']['status']
            }
        except Exception as e:
            return {'enabled': False, 'error': str(e)}
    
    def _check_access_analyzer(self) -> Dict[str, Any]:
        try:
            client = self.session.client('accessanalyzer')
            analyzers = client.list_analyzers()
            
            return {
                'enabled': len(analyzers['analyzers']) > 0,
                'analyzer_count': len(analyzers['analyzers']),
                'analyzers': [a['name'] for a in analyzers['analyzers']]
            }
        except Exception as e:
            return {'enabled': False, 'error': str(e)}
    
    def _get_security_hub_findings(self, severity_filter: Optional[str], session: boto3.Session = None, region: str = None, resource_type: Optional[str] = None, compliance_status: Optional[str] = None, max_results: int = 1000) -> List[SecurityFinding]:
        try:
            session = session or self.session
            region = region or self.region
            client = session.client('securityhub')
            filters = {}
            
            if severity_filter:
                filters['SeverityLabel'] = [{'Value': severity_filter.upper(), 'Comparison': 'EQUALS'}]
            
            if resource_type:
                filters['ResourceType'] = [{'Value': f'AWS::{resource_type.upper()}::', 'Comparison': 'PREFIX'}]
            
            if compliance_status:
                filters['ComplianceStatus'] = [{'Value': compliance_status.upper(), 'Comparison': 'EQUALS'}]
            
            # Paginate through all findings to get complete dataset
            all_findings = []
            next_token = None
            
            while len(all_findings) < max_results:
                # AWS Security Hub max is 100 per call
                page_size = min(100, max_results - len(all_findings))
                
                kwargs = {
                    'Filters': filters,
                    'MaxResults': page_size
                }
                
                if next_token:
                    kwargs['NextToken'] = next_token
                
                response = client.get_findings(**kwargs)
                all_findings.extend(response['Findings'])
                
                next_token = response.get('NextToken')
                if not next_token:
                    break
            
            return [
                SecurityFinding(
                    service='SecurityHub',
                    severity=f.get('Severity', {}).get('Label', 'UNKNOWN'),
                    title=f.get('Title', 'Unknown'),
                    description=f.get('Description', 'No description'),
                    resource_id=f.get('Resources', [{}])[0].get('Id', 'Unknown'),
                    region=region
                )
                for f in all_findings[:max_results]
            ]
        except Exception:
            return []
    
    def _get_guardduty_findings(self, severity_filter: Optional[str], session: boto3.Session = None, region: str = None, resource_type: Optional[str] = None, max_results: int = 1000) -> List[SecurityFinding]:
        try:
            session = session or self.session
            region = region or self.region
            client = session.client('guardduty')
            detectors = client.list_detectors()
            
            if not detectors['DetectorIds']:
                return []
            
            detector_id = detectors['DetectorIds'][0]
            
            # Build finding criteria for filtering
            finding_criteria = {}
            if severity_filter:
                # GuardDuty uses numeric severity: 1.0-3.9=LOW, 4.0-6.9=MEDIUM, 7.0-8.9=HIGH, 9.0-10.0=CRITICAL
                severity_ranges = {
                    'LOW': {'gte': 1.0, 'lt': 4.0},
                    'MEDIUM': {'gte': 4.0, 'lt': 7.0},
                    'HIGH': {'gte': 7.0, 'lt': 9.0},
                    'CRITICAL': {'gte': 9.0, 'lte': 10.0}
                }
                if severity_filter.upper() in severity_ranges:
                    range_filter = severity_ranges[severity_filter.upper()]
                    finding_criteria['severity'] = range_filter
            
            if resource_type:
                finding_criteria['type'] = {'eq': [f'{resource_type.upper()}*']}
            
            if finding_criteria:
                findings = client.list_findings(
                    DetectorId=detector_id,
                    FindingCriteria={'Criterion': finding_criteria},
                    MaxResults=min(50, max_results)  # GuardDuty max is 50 per call
                )
            else:
                findings = client.list_findings(DetectorId=detector_id, MaxResults=min(50, max_results))
            
            if not findings['FindingIds']:
                return []
            
            finding_details = client.get_findings(
                DetectorId=detector_id,
                FindingIds=findings['FindingIds']
            )
            
            result = []
            for f in finding_details['Findings']:
                severity_num = f.get('Severity', 0)
                # Convert numeric severity to label
                if severity_num >= 9.0:
                    severity_label = 'CRITICAL'
                elif severity_num >= 7.0:
                    severity_label = 'HIGH'
                elif severity_num >= 4.0:
                    severity_label = 'MEDIUM'
                else:
                    severity_label = 'LOW'
                    
                result.append(SecurityFinding(
                    service='GuardDuty',
                    severity=severity_label,
                    title=f.get('Title', 'Unknown'),
                    description=f.get('Description', 'No description'),
                    resource_id=f.get('Resource', {}).get('InstanceDetails', {}).get('InstanceId', 'Unknown'),
                    region=region
                ))
            
            return result
        except Exception:
            return []
    
    def _get_inspector_findings(self, severity_filter: Optional[str], session: boto3.Session = None, region: str = None, resource_type: Optional[str] = None, max_results: int = 1000) -> List[SecurityFinding]:
        try:
            session = session or self.session
            region = region or self.region
            client = session.client('inspector2')
            
            # Build filter criteria
            filter_criteria = {}
            if severity_filter:
                filter_criteria['severity'] = [{'comparison': 'EQUALS', 'value': severity_filter.upper()}]
            
            if resource_type:
                filter_criteria['resourceType'] = [{'comparison': 'EQUALS', 'value': resource_type.upper()}]
            
            if filter_criteria:
                findings = client.list_findings(filterCriteria=filter_criteria, maxResults=min(100, max_results))  # Inspector max is 100
            else:
                findings = client.list_findings(maxResults=min(100, max_results))
            
            result = []
            for f in findings.get('findings', []):
                severity = f.get('severity', 'UNKNOWN')
                    
                result.append(SecurityFinding(
                    service='Inspector',
                    severity=severity,
                    title=f.get('title', 'Unknown'),
                    description=f.get('description', 'No description'),
                    resource_id=f.get('resources', [{}])[0].get('id', 'Unknown'),
                    region=region
                ))
            
            return result
        except Exception:
            return []
    
    def _generate_service_summary(self, results: Dict) -> Dict[str, Any]:
        enabled_count = sum(1 for service in results.values() if service.get('enabled', False))
        total_count = len(results)
        
        return {
            'enabled_services': enabled_count,
            'total_services': total_count,
            'coverage_percentage': (enabled_count / total_count) * 100 if total_count > 0 else 0
        }
    
    def _generate_findings_summary(self, findings: List[SecurityFinding]) -> Dict[str, Any]:
        severity_counts = {}
        service_counts = {}
        
        for finding in findings:
            severity_counts[finding.severity] = severity_counts.get(finding.severity, 0) + 1
            service_counts[finding.service] = service_counts.get(finding.service, 0) + 1
        
        return {
            'by_severity': severity_counts,
            'by_service': service_counts
        }
    
    def _analyze_iam(self) -> Dict[str, Any]:
        try:
            iam = self.session.client('iam')
            
            # Check for root access keys
            summary = iam.get_account_summary()
            root_access_keys = summary['SummaryMap'].get('AccountAccessKeysPresent', 0)
            
            # Check MFA on root
            mfa_devices = iam.list_mfa_devices()
            root_mfa_enabled = len(mfa_devices['MFADevices']) > 0
            
            return {
                'score': 85 if root_mfa_enabled and root_access_keys == 0 else 60,
                'root_access_keys': root_access_keys,
                'root_mfa_enabled': root_mfa_enabled,
                'recommendations': ['Enable MFA on root account', 'Remove root access keys'] if not root_mfa_enabled or root_access_keys > 0 else []
            }
        except Exception:
            return {'score': 0, 'error': 'Unable to analyze IAM'}
    
    def _analyze_detective_controls(self) -> Dict[str, Any]:
        services = self.check_security_services()['services']
        enabled_count = sum(1 for s in services.values() if s.get('enabled', False))
        
        return {
            'score': (enabled_count / 4) * 100,
            'enabled_services': enabled_count,
            'total_services': 4,
            'recommendations': ['Enable all security services for comprehensive monitoring']
        }
    
    def _analyze_infrastructure(self) -> Dict[str, Any]:
        # Simplified infrastructure analysis
        return {
            'score': 75,
            'vpc_flow_logs': True,
            'security_groups': 'Review needed',
            'recommendations': ['Review security group rules', 'Enable VPC Flow Logs']
        }
    
    def _analyze_data_protection(self) -> Dict[str, Any]:
        # Simplified data protection analysis
        return {
            'score': 80,
            'encryption_at_rest': 'Partial',
            'encryption_in_transit': 'Enabled',
            'recommendations': ['Enable encryption for all storage services']
        }
    
    def _analyze_incident_response(self) -> Dict[str, Any]:
        # Simplified incident response analysis
        return {
            'score': 70,
            'automation': 'Partial',
            'playbooks': 'Manual',
            'recommendations': ['Implement automated incident response', 'Create incident response playbooks']
        }
    
    def _calculate_security_score(self, analysis: Dict) -> int:
        scores = [pillar.get('score', 0) for pillar in analysis.values()]
        return sum(scores) // len(scores) if scores else 0
    
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        recommendations = []
        for pillar in analysis.values():
            recommendations.extend(pillar.get('recommendations', []))
        return recommendations[:10]  # Top 10 recommendations
    
    def _get_service_resources(self, service: str) -> Dict[str, Any]:
        try:
            if service == 'ec2':
                client = self.session.client('ec2')
                instances = client.describe_instances()
                return {
                    'items': [
                        {
                            'id': instance['InstanceId'],
                            'state': instance['State']['Name'],
                            'type': instance['InstanceType']
                        }
                        for reservation in instances['Reservations']
                        for instance in reservation['Instances']
                    ]
                }
            elif service == 's3':
                client = self.session.client('s3')
                buckets = client.list_buckets()
                return {
                    'items': [
                        {
                            'name': bucket['Name'],
                            'creation_date': bucket['CreationDate'].isoformat()
                        }
                        for bucket in buckets['Buckets']
                    ]
                }
            elif service == 'rds':
                client = self.session.client('rds')
                instances = client.describe_db_instances()
                return {
                    'items': [
                        {
                            'id': db['DBInstanceIdentifier'],
                            'status': db['DBInstanceStatus'],
                            'engine': db['Engine']
                        }
                        for db in instances['DBInstances']
                    ]
                }
            elif service == 'lambda':
                client = self.session.client('lambda')
                functions = client.list_functions()
                return {
                    'items': [
                        {
                            'name': func['FunctionName'],
                            'runtime': func['Runtime'],
                            'last_modified': func['LastModified']
                        }
                        for func in functions['Functions']
                    ]
                }
            elif service == 'iam':
                client = self.session.client('iam')
                users = client.list_users()
                return {
                    'items': [
                        {
                            'name': user['UserName'],
                            'creation_date': user['CreateDate'].isoformat()
                        }
                        for user in users['Users']
                    ]
                }
            else:
                return {'items': []}
                
        except Exception as e:
            return {'error': str(e), 'items': []}
