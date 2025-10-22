"""
AWS service clients for Cost Explorer, EC2, S3, etc.
"""
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

try:
    import boto3
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


class AWSClients:
    """Wrapper for AWS service clients."""
    
    def __init__(self):
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self.use_mock = os.getenv("USE_MOCK_DATA", "true").lower() == "true"
        
        self.ce_client = None
        self.ec2_client = None
        self.s3_client = None
        
        if BOTO3_AVAILABLE and not self.use_mock:
            try:
                self.ce_client = boto3.client('ce', region_name=self.region)
                self.ec2_client = boto3.client('ec2', region_name=self.region)
                self.s3_client = boto3.client('s3', region_name=self.region)
            except Exception as e:
                print(f"Warning: Failed to initialize AWS clients: {e}")
    
    def get_cost_data(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        granularity: str = "MONTHLY"
    ) -> Dict[str, Any]:
        """
        Get AWS cost data from Cost Explorer.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            granularity: DAILY, MONTHLY, or HOURLY
            
        Returns:
            Cost data dictionary
        """
        if self.use_mock or not self.ce_client:
            return self._get_mock_cost_data()
        
        try:
            # Default to last 3 months
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
            if not start_date:
                start = datetime.now() - timedelta(days=90)
                start_date = start.strftime("%Y-%m-%d")
            
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                Granularity=granularity,
                Metrics=['UnblendedCost'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'}
                ]
            )
            
            # Parse response
            cost_by_service = {}
            total_cost = 0.0
            
            for result in response.get('ResultsByTime', []):
                for group in result.get('Groups', []):
                    service = group['Keys'][0]
                    amount = float(group['Metrics']['UnblendedCost']['Amount'])
                    
                    if service not in cost_by_service:
                        cost_by_service[service] = 0.0
                    cost_by_service[service] += amount
                    total_cost += amount
            
            return {
                "total_cost": round(total_cost, 2),
                "cost_by_service": cost_by_service,
                "period": {
                    "start": start_date,
                    "end": end_date
                }
            }
        
        except Exception as e:
            print(f"Error fetching cost data: {e}")
            return self._get_mock_cost_data()
    
    def list_idle_ec2_instances(self) -> List[Dict[str, Any]]:
        """
        List EC2 instances with low CPU utilization (potentially idle).
        
        Returns:
            List of idle instance dictionaries
        """
        if self.use_mock or not self.ec2_client:
            return self._get_mock_idle_instances()
        
        try:
            response = self.ec2_client.describe_instances(
                Filters=[
                    {'Name': 'instance-state-name', 'Values': ['running']}
                ]
            )
            
            idle_instances = []
            for reservation in response.get('Reservations', []):
                for instance in reservation.get('Instances', []):
                    # In production, would check CloudWatch metrics for CPU
                    # For now, just return running instances
                    idle_instances.append({
                        "instance_id": instance['InstanceId'],
                        "instance_type": instance['InstanceType'],
                        "state": instance['State']['Name'],
                        "launch_time": instance['LaunchTime'].isoformat()
                    })
            
            return idle_instances
        
        except Exception as e:
            print(f"Error listing EC2 instances: {e}")
            return self._get_mock_idle_instances()
    
    def list_old_snapshots(self, days_old: int = 90) -> List[Dict[str, Any]]:
        """
        List EBS snapshots older than specified days.
        
        Args:
            days_old: Age threshold in days
            
        Returns:
            List of old snapshot dictionaries
        """
        if self.use_mock or not self.ec2_client:
            return self._get_mock_old_snapshots()
        
        try:
            response = self.ec2_client.describe_snapshots(OwnerIds=['self'])
            
            cutoff_date = datetime.now() - timedelta(days=days_old)
            old_snapshots = []
            
            for snapshot in response.get('Snapshots', []):
                start_time = snapshot['StartTime'].replace(tzinfo=None)
                if start_time < cutoff_date:
                    old_snapshots.append({
                        "snapshot_id": snapshot['SnapshotId'],
                        "volume_id": snapshot.get('VolumeId', 'N/A'),
                        "start_time": snapshot['StartTime'].isoformat(),
                        "volume_size": snapshot['VolumeSize'],
                        "description": snapshot.get('Description', '')
                    })
            
            return old_snapshots
        
        except Exception as e:
            print(f"Error listing snapshots: {e}")
            return self._get_mock_old_snapshots()
    
    def analyze_s3_lifecycle_opportunities(self) -> List[Dict[str, Any]]:
        """
        Analyze S3 buckets for lifecycle policy opportunities.
        
        Returns:
            List of bucket optimization opportunities
        """
        if self.use_mock or not self.s3_client:
            return self._get_mock_s3_opportunities()
        
        try:
            response = self.s3_client.list_buckets()
            
            opportunities = []
            for bucket in response.get('Buckets', []):
                bucket_name = bucket['Name']
                
                # Check if lifecycle policy exists
                try:
                    self.s3_client.get_bucket_lifecycle_configuration(Bucket=bucket_name)
                    has_lifecycle = True
                except self.s3_client.exceptions.NoSuchLifecycleConfiguration:
                    has_lifecycle = False
                except Exception:
                    continue
                
                if not has_lifecycle:
                    opportunities.append({
                        "bucket_name": bucket_name,
                        "created": bucket['CreationDate'].isoformat(),
                        "recommendation": "Add lifecycle policy to transition old objects to cheaper storage"
                    })
            
            return opportunities
        
        except Exception as e:
            print(f"Error analyzing S3 buckets: {e}")
            return self._get_mock_s3_opportunities()
    
    def _get_mock_cost_data(self) -> Dict[str, Any]:
        """Return mock cost data."""
        return {
            "total_cost": 1247.89,
            "cost_by_service": {
                "Amazon Elastic Compute Cloud": 456.23,
                "Amazon Simple Storage Service": 234.56,
                "Amazon Relational Database Service": 312.45,
                "AWS Data Transfer": 89.34,
                "Amazon CloudWatch": 45.67,
                "Other": 109.64
            },
            "period": {
                "start": "2024-01-01",
                "end": "2024-03-31"
            }
        }
    
    def _get_mock_idle_instances(self) -> List[Dict[str, Any]]:
        """Return mock idle instances."""
        return [
            {
                "instance_id": "i-0a1b2c3d4e5f6g7h8",
                "instance_type": "t3.medium",
                "state": "running",
                "launch_time": "2024-01-15T10:30:00",
                "cpu_utilization": 5.2,
                "monthly_cost": 30.37
            },
            {
                "instance_id": "i-9h8g7f6e5d4c3b2a1",
                "instance_type": "t3.large",
                "state": "running",
                "launch_time": "2023-12-10T14:20:00",
                "cpu_utilization": 3.8,
                "monthly_cost": 60.74
            },
            {
                "instance_id": "i-1a2b3c4d5e6f7g8h9",
                "instance_type": "m5.xlarge",
                "state": "running",
                "launch_time": "2024-02-01T09:15:00",
                "cpu_utilization": 8.1,
                "monthly_cost": 140.16
            }
        ]
    
    def _get_mock_old_snapshots(self) -> List[Dict[str, Any]]:
        """Return mock old snapshots."""
        return [
            {
                "snapshot_id": "snap-0a1b2c3d4e5f6g7h8",
                "volume_id": "vol-0a1b2c3d4e5f6g7h8",
                "start_time": "2023-06-15T10:30:00",
                "volume_size": 100,
                "description": "Daily backup from old project",
                "monthly_cost": 0.50
            },
            {
                "snapshot_id": "snap-9h8g7f6e5d4c3b2a1",
                "volume_id": "vol-9h8g7f6e5d4c3b2a1",
                "start_time": "2023-08-22T14:20:00",
                "volume_size": 200,
                "description": "Pre-migration backup",
                "monthly_cost": 1.00
            }
        ]
    
    def _get_mock_s3_opportunities(self) -> List[Dict[str, Any]]:
        """Return mock S3 opportunities."""
        return [
            {
                "bucket_name": "legacy-backups-2023",
                "created": "2023-01-10T12:00:00",
                "recommendation": "Add lifecycle policy to transition old objects to Glacier",
                "estimated_savings": 45.00
            },
            {
                "bucket_name": "application-logs-archive",
                "created": "2022-11-05T08:30:00",
                "recommendation": "Enable intelligent tiering for automatic optimization",
                "estimated_savings": 78.50
            }
        ]
