"""
RAG (Retrieval Augmented Generation) service using Weaviate.
"""
import os
from typing import List, Dict, Any, Optional

try:
    import weaviate
    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False


class RAGService:
    """Service for document retrieval using Weaviate vector database."""
    
    def __init__(self):
        self.client = None
        self.collection_name = "AWSDocumentation"
        
        if WEAVIATE_AVAILABLE:
            try:
                weaviate_url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
                weaviate_key = os.getenv("WEAVIATE_API_KEY")
                
                if weaviate_key:
                    self.client = weaviate.Client(
                        url=weaviate_url,
                        auth_client_secret=weaviate.AuthApiKey(api_key=weaviate_key)
                    )
                else:
                    self.client = weaviate.Client(url=weaviate_url)
                
                # Initialize schema if needed
                self._initialize_schema()
            except Exception as e:
                print(f"Warning: Could not connect to Weaviate: {e}")
                self.client = None
    
    def _initialize_schema(self):
        """Initialize Weaviate schema for AWS documentation."""
        if not self.client:
            return
        
        try:
            # Check if collection exists
            schema = self.client.schema.get()
            collection_exists = any(
                c.get("class") == self.collection_name 
                for c in schema.get("classes", [])
            )
            
            if not collection_exists:
                # Create schema
                collection_schema = {
                    "class": self.collection_name,
                    "description": "AWS documentation for RAG",
                    "vectorizer": "text2vec-transformers",
                    "properties": [
                        {
                            "name": "title",
                            "dataType": ["text"],
                            "description": "Document title"
                        },
                        {
                            "name": "content",
                            "dataType": ["text"],
                            "description": "Document content"
                        },
                        {
                            "name": "service",
                            "dataType": ["text"],
                            "description": "AWS service name"
                        },
                        {
                            "name": "url",
                            "dataType": ["text"],
                            "description": "Documentation URL"
                        }
                    ]
                }
                self.client.schema.create_class(collection_schema)
                print(f"Created Weaviate collection: {self.collection_name}")
        except Exception as e:
            print(f"Error initializing schema: {e}")
    
    def seed_data(self, documents: List[Dict[str, Any]]):
        """Seed the database with initial AWS documentation."""
        if not self.client:
            print("Weaviate client not available")
            return
        
        try:
            with self.client.batch as batch:
                batch.batch_size = 100
                for doc in documents:
                    properties = {
                        "title": doc.get("title", ""),
                        "content": doc.get("content", ""),
                        "service": doc.get("service", ""),
                        "url": doc.get("url", "")
                    }
                    batch.add_data_object(
                        properties,
                        self.collection_name
                    )
            print(f"Seeded {len(documents)} documents to Weaviate")
        except Exception as e:
            print(f"Error seeding data: {e}")
    
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents."""
        if not self.client:
            # Return mock results if Weaviate is not available
            return self._get_mock_results(query, limit)
        
        try:
            result = (
                self.client.query
                .get(self.collection_name, ["title", "content", "service", "url"])
                .with_near_text({"concepts": [query]})
                .with_limit(limit)
                .do()
            )
            
            documents = []
            if result.get("data", {}).get("Get", {}).get(self.collection_name):
                for item in result["data"]["Get"][self.collection_name]:
                    documents.append({
                        "title": item.get("title", ""),
                        "content": item.get("content", ""),
                        "service": item.get("service", ""),
                        "url": item.get("url", "")
                    })
            
            return documents
        except Exception as e:
            print(f"Error searching: {e}")
            return self._get_mock_results(query, limit)
    
    def _get_mock_results(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Return mock results when Weaviate is not available."""
        mock_docs = [
            {
                "title": "AWS EC2 Instance Types",
                "content": "Amazon EC2 provides a wide selection of instance types optimized to fit different use cases. Instance types comprise varying combinations of CPU, memory, storage, and networking capacity.",
                "service": "EC2",
                "url": "https://docs.aws.amazon.com/ec2/instance-types.html"
            },
            {
                "title": "AWS Cost Management",
                "content": "AWS Cost Management helps you understand and manage your AWS costs and usage. Use AWS Cost Explorer to visualize, understand, and manage your AWS costs and usage over time.",
                "service": "Cost Management",
                "url": "https://docs.aws.amazon.com/cost-management/"
            },
            {
                "title": "AWS S3 Pricing",
                "content": "With Amazon S3, you pay only for what you use. There is no minimum fee. Pricing is based on storage, requests, and data transfer.",
                "service": "S3",
                "url": "https://aws.amazon.com/s3/pricing/"
            }
        ]
        
        return mock_docs[:limit]


def get_seed_documents() -> List[Dict[str, Any]]:
    """Get seed documents for AWS documentation."""
    return [
        {
            "title": "AWS EC2 Overview",
            "content": "Amazon Elastic Compute Cloud (Amazon EC2) provides scalable computing capacity in the Amazon Web Services (AWS) Cloud. Using Amazon EC2 eliminates your need to invest in hardware up front, so you can develop and deploy applications faster. You can use Amazon EC2 to launch as many or as few virtual servers as you need, configure security and networking, and manage storage.",
            "service": "EC2",
            "url": "https://docs.aws.amazon.com/ec2/"
        },
        {
            "title": "AWS S3 Best Practices",
            "content": "Amazon S3 best practices include using versioning for important data, implementing lifecycle policies to transition data to cheaper storage classes, using S3 Transfer Acceleration for faster uploads, and implementing proper access controls with IAM policies and bucket policies.",
            "service": "S3",
            "url": "https://docs.aws.amazon.com/s3/best-practices"
        },
        {
            "title": "AWS Cost Optimization",
            "content": "Cost optimization on AWS includes right-sizing instances, using Reserved Instances and Savings Plans, implementing auto-scaling, using Spot Instances for flexible workloads, and regularly reviewing unused resources. AWS Cost Explorer and AWS Trusted Advisor can help identify optimization opportunities.",
            "service": "Cost Management",
            "url": "https://docs.aws.amazon.com/cost-optimization"
        },
        {
            "title": "AWS Lambda Pricing",
            "content": "AWS Lambda pricing is based on the number of requests and the duration of code execution. You are charged for the total number of requests across all your functions. Duration is calculated from the time your code begins executing until it returns or terminates, rounded up to the nearest 1ms.",
            "service": "Lambda",
            "url": "https://aws.amazon.com/lambda/pricing/"
        },
        {
            "title": "AWS RDS Multi-AZ",
            "content": "Amazon RDS Multi-AZ deployments provide enhanced availability and durability for Database instances. When you provision a Multi-AZ DB Instance, Amazon RDS automatically creates a primary DB instance and synchronously replicates the data to a standby instance in a different Availability Zone.",
            "service": "RDS",
            "url": "https://docs.aws.amazon.com/rds/multi-az"
        },
        {
            "title": "AWS CloudFormation",
            "content": "AWS CloudFormation is a service that helps you model and set up your AWS resources so you can spend less time managing those resources and more time focusing on your applications. You create a template that describes all the AWS resources that you want, and CloudFormation takes care of provisioning and configuring those resources for you.",
            "service": "CloudFormation",
            "url": "https://docs.aws.amazon.com/cloudformation/"
        },
        {
            "title": "AWS VPC Setup",
            "content": "Amazon Virtual Private Cloud (Amazon VPC) lets you provision a logically isolated section of the AWS Cloud. Best practices include using multiple availability zones, implementing proper subnet design with public and private subnets, using NAT Gateways for private subnet internet access, and implementing network ACLs and security groups.",
            "service": "VPC",
            "url": "https://docs.aws.amazon.com/vpc/"
        },
        {
            "title": "AWS IAM Best Practices",
            "content": "IAM best practices include using the principle of least privilege, enabling MFA for privileged users, rotating credentials regularly, using IAM roles instead of access keys where possible, and implementing strong password policies. Regularly review and audit IAM policies and permissions.",
            "service": "IAM",
            "url": "https://docs.aws.amazon.com/iam/best-practices"
        }
    ]
