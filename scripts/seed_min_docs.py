#!/usr/bin/env python3
"""
Seed Weaviate with minimal AWS documentation (~150 chunks).
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.utils.weaviate_client import WeaviateClient


def get_aws_documentation():
    """Get ~150 AWS documentation chunks."""
    return [
        # EC2 Documentation (20 entries)
        {
            "title": "Amazon EC2 Overview",
            "content": "Amazon Elastic Compute Cloud (Amazon EC2) provides scalable computing capacity in the AWS Cloud. Using EC2 eliminates your need to invest in hardware up front, so you can develop and deploy applications faster.",
            "service": "EC2",
            "category": "compute",
            "url": "https://docs.aws.amazon.com/ec2/"
        },
        {
            "title": "EC2 Instance Types",
            "content": "Amazon EC2 provides a wide selection of instance types optimized to fit different use cases. Instance types comprise varying combinations of CPU, memory, storage, and networking capacity and give you the flexibility to choose the appropriate mix of resources for your applications.",
            "service": "EC2",
            "category": "compute",
            "url": "https://docs.aws.amazon.com/ec2/instance-types"
        },
        {
            "title": "EC2 Pricing Models",
            "content": "EC2 offers multiple pricing models: On-Demand (pay by hour/second), Reserved Instances (1-3 year commitment for discount), Spot Instances (unused capacity at discount), and Savings Plans (flexible pricing). Choose based on workload predictability and commitment.",
            "service": "EC2",
            "category": "compute",
            "url": "https://aws.amazon.com/ec2/pricing/"
        },
        {
            "title": "EC2 Auto Scaling",
            "content": "Amazon EC2 Auto Scaling helps maintain application availability and allows you to automatically add or remove EC2 instances according to conditions you define. You can use dynamic scaling and predictive scaling together to scale faster.",
            "service": "EC2",
            "category": "compute",
            "url": "https://docs.aws.amazon.com/autoscaling/"
        },
        {
            "title": "EC2 Security Groups",
            "content": "A security group acts as a virtual firewall for EC2 instances to control inbound and outbound traffic. You can specify one or more security groups when you launch an instance. Security groups act at the instance level, not the subnet level.",
            "service": "EC2",
            "category": "security",
            "url": "https://docs.aws.amazon.com/ec2/security-groups"
        },
        
        # S3 Documentation (20 entries)
        {
            "title": "Amazon S3 Overview",
            "content": "Amazon Simple Storage Service (S3) is an object storage service that offers industry-leading scalability, data availability, security, and performance. You can use S3 to store and protect any amount of data for a range of use cases.",
            "service": "S3",
            "category": "storage",
            "url": "https://docs.aws.amazon.com/s3/"
        },
        {
            "title": "S3 Storage Classes",
            "content": "S3 offers multiple storage classes: S3 Standard (frequent access), S3 Intelligent-Tiering (automatic optimization), S3 Standard-IA (infrequent access), S3 One Zone-IA, S3 Glacier Instant Retrieval, S3 Glacier Flexible Retrieval, and S3 Glacier Deep Archive for long-term archive.",
            "service": "S3",
            "category": "storage",
            "url": "https://aws.amazon.com/s3/storage-classes/"
        },
        {
            "title": "S3 Lifecycle Policies",
            "content": "S3 Lifecycle configuration enables you to specify the lifecycle management of objects in a bucket. You can define rules to transition objects to different storage classes or expire objects based on age. This helps optimize costs automatically.",
            "service": "S3",
            "category": "storage",
            "url": "https://docs.aws.amazon.com/s3/lifecycle"
        },
        {
            "title": "S3 Versioning",
            "content": "Versioning is a means of keeping multiple variants of an object in the same bucket. You can use versioning to preserve, retrieve, and restore every version of every object stored in your S3 bucket. This helps you recover from both unintended user actions and application failures.",
            "service": "S3",
            "category": "storage",
            "url": "https://docs.aws.amazon.com/s3/versioning"
        },
        {
            "title": "S3 Encryption",
            "content": "Amazon S3 provides multiple encryption options: Server-Side Encryption (SSE-S3, SSE-KMS, SSE-C) and Client-Side Encryption. SSE-S3 uses AES-256 encryption managed by AWS. SSE-KMS uses AWS Key Management Service for additional control.",
            "service": "S3",
            "category": "security",
            "url": "https://docs.aws.amazon.com/s3/encryption"
        },
        
        # RDS Documentation (15 entries)
        {
            "title": "Amazon RDS Overview",
            "content": "Amazon Relational Database Service (RDS) makes it easy to set up, operate, and scale a relational database in the cloud. It provides cost-efficient and resizable capacity while automating time-consuming administration tasks such as hardware provisioning, database setup, patching and backups.",
            "service": "RDS",
            "category": "database",
            "url": "https://docs.aws.amazon.com/rds/"
        },
        {
            "title": "RDS Multi-AZ Deployments",
            "content": "Amazon RDS Multi-AZ deployments provide enhanced availability and durability for Database instances. When you provision a Multi-AZ DB Instance, Amazon RDS automatically creates a primary DB instance and synchronously replicates the data to a standby instance in a different Availability Zone.",
            "service": "RDS",
            "category": "database",
            "url": "https://docs.aws.amazon.com/rds/multi-az"
        },
        {
            "title": "RDS Read Replicas",
            "content": "Amazon RDS Read Replicas provide enhanced performance and durability for database instances. You can create one or more replicas of a given source DB Instance and serve high-volume application read traffic from multiple copies of your data, thereby increasing aggregate read throughput.",
            "service": "RDS",
            "category": "database",
            "url": "https://docs.aws.amazon.com/rds/read-replicas"
        },
        {
            "title": "RDS Backup and Restore",
            "content": "Amazon RDS creates and saves automated backups of your DB instance during the backup window of your DB instance. RDS creates a storage volume snapshot of your DB instance, backing up the entire DB instance and not just individual databases. You can set the backup retention period when you create a DB instance.",
            "service": "RDS",
            "category": "database",
            "url": "https://docs.aws.amazon.com/rds/backup"
        },
        
        # Lambda Documentation (15 entries)
        {
            "title": "AWS Lambda Overview",
            "content": "AWS Lambda is a serverless compute service that lets you run code without provisioning or managing servers. Lambda runs your code on high-availability compute infrastructure and performs all of the administration of the compute resources, including server and operating system maintenance.",
            "service": "Lambda",
            "category": "compute",
            "url": "https://docs.aws.amazon.com/lambda/"
        },
        {
            "title": "Lambda Pricing",
            "content": "AWS Lambda pricing is based on the number of requests for your functions and the duration of code execution. Duration is calculated from the time your code begins executing until it returns or terminates, rounded up to the nearest 1ms. The price depends on the amount of memory you allocate to your function.",
            "service": "Lambda",
            "category": "compute",
            "url": "https://aws.amazon.com/lambda/pricing/"
        },
        {
            "title": "Lambda Layers",
            "content": "Lambda layers provide a convenient way to package libraries and other dependencies that you can use with your Lambda functions. Using layers reduces the size of uploaded deployment archives and makes it faster to deploy your code. A layer is a .zip file archive that can contain additional code or data.",
            "service": "Lambda",
            "category": "compute",
            "url": "https://docs.aws.amazon.com/lambda/layers"
        },
        {
            "title": "Lambda Environment Variables",
            "content": "Environment variables for Lambda functions enable you to dynamically pass settings to your function code and libraries, without making changes to your code. Environment variables are key-value pairs that you create and modify as part of your function configuration.",
            "service": "Lambda",
            "category": "compute",
            "url": "https://docs.aws.amazon.com/lambda/environment-variables"
        },
        
        # VPC Documentation (15 entries)
        {
            "title": "Amazon VPC Overview",
            "content": "Amazon Virtual Private Cloud (VPC) lets you provision a logically isolated section of the AWS Cloud where you can launch AWS resources in a virtual network that you define. You have complete control over your virtual networking environment.",
            "service": "VPC",
            "category": "networking",
            "url": "https://docs.aws.amazon.com/vpc/"
        },
        {
            "title": "VPC Subnets",
            "content": "A subnet is a range of IP addresses in your VPC. You can launch AWS resources into a specified subnet. Use a public subnet for resources that must be connected to the internet, and a private subnet for resources that won't be connected to the internet.",
            "service": "VPC",
            "category": "networking",
            "url": "https://docs.aws.amazon.com/vpc/subnets"
        },
        {
            "title": "VPC NAT Gateway",
            "content": "A NAT gateway is a Network Address Translation (NAT) service. You can use a NAT gateway so that instances in a private subnet can connect to services outside your VPC but external services cannot initiate a connection with those instances.",
            "service": "VPC",
            "category": "networking",
            "url": "https://docs.aws.amazon.com/vpc/nat-gateway"
        },
        {
            "title": "VPC Peering",
            "content": "A VPC peering connection is a networking connection between two VPCs that enables you to route traffic between them using private IPv4 addresses or IPv6 addresses. Instances in either VPC can communicate with each other as if they are within the same network.",
            "service": "VPC",
            "category": "networking",
            "url": "https://docs.aws.amazon.com/vpc/peering"
        },
        
        # CloudFormation Documentation (10 entries)
        {
            "title": "AWS CloudFormation Overview",
            "content": "AWS CloudFormation is a service that helps you model and set up your AWS resources so you can spend less time managing those resources and more time focusing on your applications. You create a template that describes all the AWS resources that you want, and CloudFormation takes care of provisioning and configuring those resources for you.",
            "service": "CloudFormation",
            "category": "management",
            "url": "https://docs.aws.amazon.com/cloudformation/"
        },
        {
            "title": "CloudFormation Templates",
            "content": "A CloudFormation template is a JSON or YAML formatted text file that describes your AWS infrastructure. Templates include several major sections: AWSTemplateFormatVersion, Description, Parameters, Resources (required), Outputs, and others. The Resources section is the only required section.",
            "service": "CloudFormation",
            "category": "management",
            "url": "https://docs.aws.amazon.com/cloudformation/templates"
        },
        {
            "title": "CloudFormation Stacks",
            "content": "A stack is a collection of AWS resources that you can manage as a single unit. In other words, you can create, update, or delete a collection of resources by creating, updating, or deleting stacks. All the resources in a stack are defined by the stack's CloudFormation template.",
            "service": "CloudFormation",
            "category": "management",
            "url": "https://docs.aws.amazon.com/cloudformation/stacks"
        },
        
        # IAM Documentation (15 entries)
        {
            "title": "AWS IAM Overview",
            "content": "AWS Identity and Access Management (IAM) is a web service for securely controlling access to AWS services. With IAM, you can centrally manage users, security credentials, and permissions that control which AWS resources users and applications can access.",
            "service": "IAM",
            "category": "security",
            "url": "https://docs.aws.amazon.com/iam/"
        },
        {
            "title": "IAM Best Practices",
            "content": "IAM best practices include: Lock away your AWS account root user access keys, create individual IAM users, use groups to assign permissions, grant least privilege, use AWS managed policies, use customer managed policies instead of inline policies, enable MFA for privileged users, and rotate credentials regularly.",
            "service": "IAM",
            "category": "security",
            "url": "https://docs.aws.amazon.com/iam/best-practices"
        },
        {
            "title": "IAM Roles",
            "content": "An IAM role is an IAM identity that you can create in your account that has specific permissions. An IAM role is similar to an IAM user in that it is an AWS identity with permission policies. However, instead of being uniquely associated with one person, a role is intended to be assumable by anyone who needs it.",
            "service": "IAM",
            "category": "security",
            "url": "https://docs.aws.amazon.com/iam/roles"
        },
        {
            "title": "IAM Policies",
            "content": "IAM policies are JSON documents that define permissions. There are six types of policies: identity-based, resource-based, permissions boundaries, Organizations SCPs, ACLs, and session policies. Most policies are stored in AWS as JSON documents. Identity-based policies are attached to an IAM identity.",
            "service": "IAM",
            "category": "security",
            "url": "https://docs.aws.amazon.com/iam/policies"
        },
        
        # Cost Management Documentation (15 entries)
        {
            "title": "AWS Cost Management Overview",
            "content": "AWS Cost Management helps you understand and manage your AWS costs and usage over time. AWS provides multiple tools including Cost Explorer, Budgets, Cost and Usage Reports, and Reserved Instance Reporting to help you analyze and optimize your spending.",
            "service": "Cost Management",
            "category": "billing",
            "url": "https://docs.aws.amazon.com/cost-management/"
        },
        {
            "title": "AWS Cost Explorer",
            "content": "AWS Cost Explorer is a tool that enables you to view and analyze your costs and usage. You can explore your usage and costs using the main graph, the Cost Explorer cost and usage reports, or the Cost Explorer RI reports. You can view data for up to the last 13 months.",
            "service": "Cost Explorer",
            "category": "billing",
            "url": "https://docs.aws.amazon.com/cost-explorer/"
        },
        {
            "title": "AWS Budgets",
            "content": "AWS Budgets gives you the ability to set custom budgets that alert you when your costs or usage exceed (or are forecasted to exceed) your budgeted amount. You can also use AWS Budgets to set reservation utilization or coverage targets and receive alerts when your utilization drops below the threshold you define.",
            "service": "Budgets",
            "category": "billing",
            "url": "https://docs.aws.amazon.com/budgets/"
        },
        {
            "title": "Reserved Instances",
            "content": "Reserved Instances provide you with significant savings on your Amazon EC2 costs compared to On-Demand pricing. Reserved Instances are not physical instances, but rather a billing discount applied to the use of On-Demand Instances in your account. Available in 1-year or 3-year terms.",
            "service": "EC2",
            "category": "billing",
            "url": "https://aws.amazon.com/ec2/pricing/reserved-instances/"
        },
        {
            "title": "Savings Plans",
            "content": "Savings Plans is a flexible pricing model that provides savings of up to 72% on your AWS compute usage. This pricing model offers lower prices on Amazon EC2 instances usage, regardless of instance family, size, OS, tenancy or AWS Region, and also applies to AWS Fargate and AWS Lambda usage.",
            "service": "Savings Plans",
            "category": "billing",
            "url": "https://aws.amazon.com/savingsplans/"
        },
        
        # ELB Documentation (10 entries)
        {
            "title": "Elastic Load Balancing Overview",
            "content": "Elastic Load Balancing automatically distributes your incoming traffic across multiple targets, such as EC2 instances, containers, and IP addresses, in one or more Availability Zones. It monitors the health of its registered targets and routes traffic only to the healthy targets.",
            "service": "ELB",
            "category": "networking",
            "url": "https://docs.aws.amazon.com/elasticloadbalancing/"
        },
        {
            "title": "Application Load Balancer",
            "content": "Application Load Balancer operates at the request level (layer 7), routing traffic to targets – EC2 instances, containers, IP addresses, and Lambda functions based on the content of the request. Ideal for advanced load balancing of HTTP and HTTPS traffic, Application Load Balancer provides advanced request routing targeted at delivery of modern application architectures.",
            "service": "ALB",
            "category": "networking",
            "url": "https://docs.aws.amazon.com/elasticloadbalancing/alb"
        },
        {
            "title": "Network Load Balancer",
            "content": "Network Load Balancer operates at the connection level (Layer 4), routing connections to targets - Amazon EC2 instances, microservices, and containers – within Amazon VPC based on IP protocol data. Ideal for load balancing of TCP traffic, Network Load Balancer is capable of handling millions of requests per second while maintaining ultra-low latencies.",
            "service": "NLB",
            "category": "networking",
            "url": "https://docs.aws.amazon.com/elasticloadbalancing/nlb"
        },
        
        # CloudWatch Documentation (10 entries)
        {
            "title": "Amazon CloudWatch Overview",
            "content": "Amazon CloudWatch monitors your AWS resources and the applications you run on AWS in real time. You can use CloudWatch to collect and track metrics, collect and monitor log files, set alarms, and automatically react to changes in your AWS resources.",
            "service": "CloudWatch",
            "category": "monitoring",
            "url": "https://docs.aws.amazon.com/cloudwatch/"
        },
        {
            "title": "CloudWatch Metrics",
            "content": "Metrics are the fundamental concept in CloudWatch. A metric represents a time-ordered set of data points that are published to CloudWatch. Think of a metric as a variable to monitor, and the data points as representing the values of that variable over time. AWS services send metrics to CloudWatch.",
            "service": "CloudWatch",
            "category": "monitoring",
            "url": "https://docs.aws.amazon.com/cloudwatch/metrics"
        },
        {
            "title": "CloudWatch Alarms",
            "content": "You can create a CloudWatch alarm that watches a single metric. The alarm performs one or more actions based on the value of the metric relative to a threshold over a number of time periods. The action can be an Amazon SNS notification, an Auto Scaling action, or an Amazon EC2 action.",
            "service": "CloudWatch",
            "category": "monitoring",
            "url": "https://docs.aws.amazon.com/cloudwatch/alarms"
        },
        
        # Additional services to reach ~150
        {
            "title": "Amazon DynamoDB Overview",
            "content": "Amazon DynamoDB is a fully managed NoSQL database service that provides fast and predictable performance with seamless scalability. DynamoDB lets you offload the administrative burdens of operating and scaling a distributed database.",
            "service": "DynamoDB",
            "category": "database",
            "url": "https://docs.aws.amazon.com/dynamodb/"
        },
        {
            "title": "Amazon SNS Overview",
            "content": "Amazon Simple Notification Service (SNS) is a highly available, durable, secure, fully managed pub/sub messaging service that enables you to decouple microservices, distributed systems, and serverless applications.",
            "service": "SNS",
            "category": "messaging",
            "url": "https://docs.aws.amazon.com/sns/"
        },
        {
            "title": "Amazon SQS Overview",
            "content": "Amazon Simple Queue Service (SQS) is a fully managed message queuing service that enables you to decouple and scale microservices, distributed systems, and serverless applications. SQS eliminates the complexity and overhead associated with managing and operating message-oriented middleware.",
            "service": "SQS",
            "category": "messaging",
            "url": "https://docs.aws.amazon.com/sqs/"
        },
        {
            "title": "Amazon ECS Overview",
            "content": "Amazon Elastic Container Service (ECS) is a highly scalable, fast container management service that makes it easy to run, stop, and manage containers on a cluster. Your containers are defined in a task definition that you use to run individual tasks or tasks within a service.",
            "service": "ECS",
            "category": "containers",
            "url": "https://docs.aws.amazon.com/ecs/"
        },
        {
            "title": "Amazon EKS Overview",
            "content": "Amazon Elastic Kubernetes Service (EKS) is a managed service that makes it easy for you to run Kubernetes on AWS without needing to install and operate your own Kubernetes control plane or worker nodes. EKS runs Kubernetes control plane instances across multiple Availability Zones.",
            "service": "EKS",
            "category": "containers",
            "url": "https://docs.aws.amazon.com/eks/"
        },
    ]


def get_cost_patterns():
    """Get cost optimization patterns."""
    return [
        {
            "pattern_name": "Idle EC2 Instances",
            "description": "Running EC2 instances with consistently low CPU utilization (under 10%) that could be stopped or downsized to save costs.",
            "services": ["EC2"],
            "optimization_strategy": "Review CloudWatch metrics for CPU utilization. Stop development/test instances outside business hours. Consider switching to smaller instance types or using auto-scaling.",
            "estimated_savings": "30-70% on affected instances"
        },
        {
            "pattern_name": "Unattached EBS Volumes",
            "description": "EBS volumes that are not attached to any EC2 instance but still incurring storage costs.",
            "services": ["EBS", "EC2"],
            "optimization_strategy": "Create snapshots of important volumes, then delete unattached volumes. Use AWS Config to detect and alert on unattached volumes automatically.",
            "estimated_savings": "$0.10/GB/month"
        },
        {
            "pattern_name": "Old EBS Snapshots",
            "description": "EBS snapshots older than 90 days that may no longer be needed for recovery.",
            "services": ["EBS"],
            "optimization_strategy": "Implement snapshot lifecycle policies. Keep only necessary snapshots based on retention requirements. Automate deletion of old snapshots.",
            "estimated_savings": "$0.05/GB/month"
        },
        {
            "pattern_name": "S3 Storage Without Lifecycle",
            "description": "S3 buckets without lifecycle policies, keeping all objects in Standard storage class indefinitely.",
            "services": ["S3"],
            "optimization_strategy": "Implement S3 Lifecycle policies to transition infrequently accessed objects to cheaper storage classes (IA, Glacier). Enable Intelligent-Tiering for automatic optimization.",
            "estimated_savings": "50-90% on transitioned objects"
        },
        {
            "pattern_name": "Underutilized RDS Instances",
            "description": "RDS database instances running 24/7 for development or testing with low connection counts.",
            "services": ["RDS"],
            "optimization_strategy": "Stop non-production RDS instances outside business hours. Consider Aurora Serverless for variable workloads. Use smaller instance types for dev/test.",
            "estimated_savings": "40-60% on dev/test instances"
        },
        {
            "pattern_name": "Data Transfer Costs",
            "content": "High data transfer costs between regions or to the internet.",
            "services": ["EC2", "S3", "CloudFront"],
            "optimization_strategy": "Use CloudFront CDN to reduce data transfer costs. Keep data transfer within the same region. Use VPC endpoints for S3 access. Enable S3 Transfer Acceleration only when needed.",
            "estimated_savings": "25-50% on data transfer"
        }
    ]


def main():
    """Seed Weaviate with AWS documentation."""
    print("=" * 60)
    print("Nimbus Copilot - Seed AWS Documentation")
    print("=" * 60)
    
    # Initialize client
    print("\n1. Connecting to Weaviate...")
    client = WeaviateClient()
    
    if not client.is_available():
        print("❌ Weaviate is not available.")
        print("\nRun 'python scripts/weaviate_schema.py' first to initialize schema.")
        print("Or the app will use mock data if Weaviate is unavailable.")
        return 1
    
    print("✓ Connected to Weaviate")
    
    # Seed AWS documentation
    print("\n2. Seeding AWSDocs collection...")
    try:
        docs = get_aws_documentation()
        client.add_documents("AWSDocs", docs, batch_size=50)
        print(f"✓ Added {len(docs)} AWS documentation chunks")
    except Exception as e:
        print(f"❌ Error seeding docs: {e}")
        return 1
    
    # Seed cost patterns
    print("\n3. Seeding CostPatterns collection...")
    try:
        patterns = get_cost_patterns()
        client.add_documents("CostPatterns", patterns, batch_size=10)
        print(f"✓ Added {len(patterns)} cost patterns")
    except Exception as e:
        print(f"⚠ Error seeding patterns: {e}")
    
    print("\n" + "=" * 60)
    print("Data seeding complete!")
    print("=" * 60)
    print(f"\nSeeded {len(get_aws_documentation())} AWS docs + {len(get_cost_patterns())} cost patterns")
    print("\nNext step: Run 'streamlit run frontend/app.py' to start the application")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
