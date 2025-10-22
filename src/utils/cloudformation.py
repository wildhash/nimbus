"""
CloudFormation template generation utilities.
"""
import yaml
from typing import Dict, Any, List


class CloudFormationGenerator:
    """Generate CloudFormation templates from infrastructure descriptions."""
    
    def generate_template(
        self,
        description: str,
        resources: List[Dict[str, Any]]
    ) -> str:
        """
        Generate a CloudFormation template.
        
        Args:
            description: Template description
            resources: List of resource specifications
            
        Returns:
            YAML CloudFormation template as string
        """
        template = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": description,
            "Parameters": self._generate_parameters(resources),
            "Resources": self._generate_resources(resources),
            "Outputs": self._generate_outputs(resources)
        }
        
        return yaml.dump(template, default_flow_style=False, sort_keys=False)
    
    def _generate_parameters(self, resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate CloudFormation parameters."""
        parameters = {
            "EnvironmentName": {
                "Description": "Environment name prefix",
                "Type": "String",
                "Default": "dev"
            }
        }
        
        # Add resource-specific parameters
        for resource in resources:
            if resource.get("type") == "EC2":
                parameters["InstanceType"] = {
                    "Description": "EC2 instance type",
                    "Type": "String",
                    "Default": "t3.micro",
                    "AllowedValues": ["t3.micro", "t3.small", "t3.medium"]
                }
            elif resource.get("type") == "RDS":
                parameters["DBInstanceClass"] = {
                    "Description": "RDS instance class",
                    "Type": "String",
                    "Default": "db.t3.micro"
                }
        
        return parameters
    
    def _generate_resources(self, resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate CloudFormation resources."""
        cfn_resources = {}
        
        for i, resource in enumerate(resources):
            resource_type = resource.get("type", "")
            resource_name = resource.get("name", f"Resource{i}")
            
            if resource_type == "VPC":
                cfn_resources[resource_name] = self._create_vpc_resource()
            elif resource_type == "EC2":
                cfn_resources[resource_name] = self._create_ec2_resource()
            elif resource_type == "S3":
                cfn_resources[resource_name] = self._create_s3_resource()
            elif resource_type == "RDS":
                cfn_resources[resource_name] = self._create_rds_resource()
        
        return cfn_resources
    
    def _generate_outputs(self, resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate CloudFormation outputs."""
        outputs = {}
        
        for resource in resources:
            resource_type = resource.get("type", "")
            resource_name = resource.get("name", "")
            
            if resource_type == "EC2":
                outputs[f"{resource_name}PublicIP"] = {
                    "Description": f"Public IP of {resource_name}",
                    "Value": {"Fn::GetAtt": [resource_name, "PublicIp"]}
                }
            elif resource_type == "S3":
                outputs[f"{resource_name}BucketName"] = {
                    "Description": f"Name of S3 bucket {resource_name}",
                    "Value": {"Ref": resource_name}
                }
        
        return outputs
    
    def _create_vpc_resource(self) -> Dict[str, Any]:
        """Create a VPC resource."""
        return {
            "Type": "AWS::EC2::VPC",
            "Properties": {
                "CidrBlock": "10.0.0.0/16",
                "EnableDnsHostnames": True,
                "EnableDnsSupport": True,
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": {"Fn::Sub": "${EnvironmentName}-VPC"}
                    }
                ]
            }
        }
    
    def _create_ec2_resource(self) -> Dict[str, Any]:
        """Create an EC2 instance resource."""
        return {
            "Type": "AWS::EC2::Instance",
            "Properties": {
                "InstanceType": {"Ref": "InstanceType"},
                "ImageId": "ami-0c55b159cbfafe1f0",  # Amazon Linux 2 (example)
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": {"Fn::Sub": "${EnvironmentName}-Instance"}
                    }
                ]
            }
        }
    
    def _create_s3_resource(self) -> Dict[str, Any]:
        """Create an S3 bucket resource."""
        return {
            "Type": "AWS::S3::Bucket",
            "Properties": {
                "BucketName": {"Fn::Sub": "${EnvironmentName}-bucket-${AWS::AccountId}"},
                "VersioningConfiguration": {
                    "Status": "Enabled"
                },
                "PublicAccessBlockConfiguration": {
                    "BlockPublicAcls": True,
                    "BlockPublicPolicy": True,
                    "IgnorePublicAcls": True,
                    "RestrictPublicBuckets": True
                }
            }
        }
    
    def _create_rds_resource(self) -> Dict[str, Any]:
        """Create an RDS database resource."""
        return {
            "Type": "AWS::RDS::DBInstance",
            "Properties": {
                "DBInstanceClass": {"Ref": "DBInstanceClass"},
                "Engine": "postgres",
                "MasterUsername": "admin",
                "MasterUserPassword": "ChangeMe123!",  # Should use Secrets Manager
                "AllocatedStorage": "20",
                "DBInstanceIdentifier": {"Fn::Sub": "${EnvironmentName}-db"}
            }
        }
    
    def parse_infrastructure_desc(self, description: str) -> List[Dict[str, Any]]:
        """Parse infrastructure description into resource list."""
        resources = []
        
        # Simple keyword-based parsing
        desc_lower = description.lower()
        
        if "vpc" in desc_lower or "network" in desc_lower:
            resources.append({"type": "VPC", "name": "MainVPC"})
        
        if "ec2" in desc_lower or "instance" in desc_lower or "server" in desc_lower:
            resources.append({"type": "EC2", "name": "WebServer"})
        
        if "s3" in desc_lower or "bucket" in desc_lower or "storage" in desc_lower:
            resources.append({"type": "S3", "name": "DataBucket"})
        
        if "rds" in desc_lower or "database" in desc_lower:
            resources.append({"type": "RDS", "name": "Database"})
        
        return resources
    
    def generate_from_description(self, description: str) -> str:
        """Generate CloudFormation template from natural language description."""
        resources = self.parse_infrastructure_desc(description)
        
        if not resources:
            # Default template
            resources = [
                {"type": "VPC", "name": "MainVPC"},
                {"type": "EC2", "name": "WebServer"}
            ]
        
        return self.generate_template(
            description=description,
            resources=resources
        )
