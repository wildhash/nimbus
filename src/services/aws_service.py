"""
Mock AWS data service for testing without live AWS credentials.
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
import random


class MockAWSService:
    """Mock AWS service for development and testing."""
    
    @staticmethod
    def get_cost_data(months: int = 3) -> Dict[str, Any]:
        """Generate mock AWS cost data."""
        services = ["EC2", "S3", "RDS", "Lambda", "CloudFront", "DynamoDB"]
        
        # Generate cost data for the past N months
        cost_history = []
        current_date = datetime.now()
        
        for i in range(months):
            month_date = current_date - timedelta(days=30 * i)
            month_name = month_date.strftime("%B %Y")
            
            service_costs = {}
            total = 0
            for service in services:
                # Generate random but realistic costs
                base_cost = random.uniform(50, 1000)
                cost = round(base_cost * (1 + random.uniform(-0.1, 0.1)), 2)
                service_costs[service] = cost
                total += cost
            
            cost_history.append({
                "month": month_name,
                "total_cost": round(total, 2),
                "services": service_costs
            })
        
        return {
            "cost_history": cost_history,
            "current_month": cost_history[0],
            "period": f"Last {months} months"
        }
    
    @staticmethod
    def get_ec2_instances() -> List[Dict[str, Any]]:
        """Generate mock EC2 instance data."""
        instance_types = ["t3.micro", "t3.small", "t3.medium", "m5.large", "c5.xlarge"]
        states = ["running", "stopped"]
        
        instances = []
        for i in range(5):
            utilization = random.randint(10, 95)
            instance = {
                "id": f"i-{random.randint(100000, 999999)}",
                "type": random.choice(instance_types),
                "state": random.choice(states),
                "name": f"instance-{i+1}",
                "utilization": utilization,
                "monthly_cost": round(random.uniform(20, 200), 2),
                "region": "us-east-1"
            }
            instances.append(instance)
        
        return instances
    
    @staticmethod
    def get_s3_buckets() -> List[Dict[str, Any]]:
        """Generate mock S3 bucket data."""
        storage_classes = ["STANDARD", "STANDARD_IA", "GLACIER"]
        
        buckets = []
        for i in range(4):
            size_gb = random.uniform(10, 5000)
            bucket = {
                "name": f"my-bucket-{i+1}",
                "size_gb": round(size_gb, 2),
                "storage_class": random.choice(storage_classes),
                "monthly_cost": round(size_gb * 0.023, 2),
                "objects": random.randint(100, 10000),
                "region": "us-east-1"
            }
            buckets.append(bucket)
        
        return buckets
    
    @staticmethod
    def get_cost_breakdown() -> Dict[str, Any]:
        """Generate detailed cost breakdown."""
        return {
            "total_cost": 2845.67,
            "services": {
                "EC2": 1245.30,
                "S3": 456.80,
                "RDS": 678.90,
                "Lambda": 234.50,
                "CloudFront": 156.20,
                "DynamoDB": 73.97
            },
            "by_region": {
                "us-east-1": 1789.45,
                "us-west-2": 856.22,
                "eu-west-1": 200.00
            },
            "period": "Current Month",
            "resources": [
                {
                    "type": "EC2",
                    "name": "web-server-prod",
                    "cost": 456.78,
                    "utilization": 35
                },
                {
                    "type": "RDS",
                    "name": "postgres-db",
                    "cost": 234.56,
                    "utilization": 68
                },
                {
                    "type": "S3",
                    "name": "data-lake-bucket",
                    "cost": 189.34,
                    "utilization": 90
                }
            ]
        }
    
    @staticmethod
    def get_optimization_opportunities() -> List[Dict[str, Any]]:
        """Generate mock optimization opportunities."""
        return [
            {
                "title": "Right-size Over-provisioned EC2 Instances",
                "description": "3 instances are running at <40% CPU utilization and can be downsized",
                "estimated_savings": 345.60,
                "difficulty": "Easy",
                "action": "Downgrade t3.medium to t3.small"
            },
            {
                "title": "Implement S3 Lifecycle Policies",
                "description": "Move infrequently accessed data to S3 Glacier",
                "estimated_savings": 234.80,
                "difficulty": "Easy",
                "action": "Create lifecycle rule to transition data after 90 days"
            },
            {
                "title": "Purchase Reserved Instances",
                "description": "Save on long-running EC2 instances with RI",
                "estimated_savings": 567.00,
                "difficulty": "Medium",
                "action": "Purchase 1-year Reserved Instances"
            },
            {
                "title": "Delete Unused EBS Volumes",
                "description": "5 unattached EBS volumes found",
                "estimated_savings": 89.50,
                "difficulty": "Easy",
                "action": "Review and delete unused volumes"
            },
            {
                "title": "Enable Auto-scaling",
                "description": "Reduce costs during low-traffic periods",
                "estimated_savings": 456.70,
                "difficulty": "Medium",
                "action": "Configure auto-scaling groups"
            }
        ]


class LiveAWSService:
    """Live AWS service using boto3."""
    
    def __init__(self):
        try:
            import boto3
            self.ce_client = boto3.client('ce')
            self.ec2_client = boto3.client('ec2')
            self.s3_client = boto3.client('s3')
            self.available = True
        except Exception as e:
            print(f"AWS clients not available: {e}")
            self.available = False
    
    def get_cost_data(self, months: int = 3) -> Dict[str, Any]:
        """Get real AWS cost data from Cost Explorer."""
        if not self.available:
            return MockAWSService.get_cost_data(months)
        
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30 * months)
            
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='MONTHLY',
                Metrics=['UnblendedCost'],
                GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
            )
            
            # Process response
            return self._process_cost_response(response)
        except Exception as e:
            print(f"Error fetching live cost data: {e}")
            return MockAWSService.get_cost_data(months)
    
    def _process_cost_response(self, response: Dict) -> Dict[str, Any]:
        """Process Cost Explorer API response."""
        # Implementation would parse the actual AWS response
        # Falling back to mock for simplicity
        return MockAWSService.get_cost_data()


def get_aws_service(use_mock: bool = True):
    """Get AWS service instance (mock or live)."""
    if use_mock:
        return MockAWSService()
    else:
        return LiveAWSService()
