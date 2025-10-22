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
    
    def hybrid_search(self, query: str, k: int = 3) -> List[Dict[str, str]]:
        """
        Perform hybrid search and return results with title, url, and snippet.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of dicts with keys: title, url, snippet
        """
        # If WEAVIATE_URL is missing or client unavailable, use curated stubs
        if os.getenv("WEAVIATE_URL", "") == "" or not self.client:
            documents = self._get_mock_results(query, k)
        else:
            # Use existing search method
            documents = self.search(query, limit=k)
        
        # Format results with snippets
        results = []
        for doc in documents:
            # Extract a short snippet (first 150 chars)
            content = doc.get("content", "")
            snippet = content[:150] + "..." if len(content) > 150 else content
            
            results.append({
                "title": doc.get("title", "Untitled"),
                "url": doc.get("url", ""),
                "snippet": snippet
            })
        
        return results
    
    def _get_mock_results(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Return mock results when Weaviate is not available."""
        # Use curated stubs for offline demo
        mock_docs = get_curated_stubs()
        
        # Simple keyword matching for relevance
        query_lower = query.lower()
        scored_docs = []
        for doc in mock_docs:
            score = 0
            if query_lower in doc["title"].lower():
                score += 10
            if query_lower in doc["content"].lower():
                score += 5
            scored_docs.append((score, doc))
        
        # Sort by score and return top results
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored_docs[:limit]]


def format_citations(hits: List[Dict[str, str]]) -> str:
    """
    Format search results as citations with bullet points and quotes.
    
    Args:
        hits: List of search results with title, url, snippet
        
    Returns:
        Formatted citation string
    """
    if not hits:
        return "No citations available."
    
    citations = []
    for i, hit in enumerate(hits[:3], 1):  # Limit to top 3
        title = hit.get("title", "Unknown")
        url = hit.get("url", "")
        snippet = hit.get("snippet", "")
        
        citation = f"**{i}. [{title}]({url})**"
        if snippet:
            citation += f"\n   > \"{snippet}\""
        citations.append(citation)
    
    return "\n\n".join(citations)


def get_curated_stubs() -> List[Dict[str, Any]]:
    """
    Get curated stub documents for offline demo (100-200 short chunks).
    These are used when Weaviate is not available.
    """
    return [
        {
            "title": "AWS EC2 Instance Types",
            "content": "Amazon EC2 provides a wide selection of instance types optimized to fit different use cases. Instance types comprise varying combinations of CPU, memory, storage, and networking capacity.",
            "service": "EC2",
            "url": "https://docs.aws.amazon.com/ec2/instance-types.html"
        },
        {
            "title": "Lambda Cold Start Tips",
            "content": "Reduce AWS Lambda cold starts by using Provisioned Concurrency, smaller deployment packages, keeping functions warm, and choosing languages with faster startup times.",
            "service": "Lambda",
            "url": "https://docs.aws.amazon.com/lambda/latest/dg/provisioned-concurrency.html"
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
        },
        {
            "title": "ALB vs NLB: When to Use Which",
            "content": "Use Application Load Balancer (ALB) for HTTP/HTTPS and Layer 7 features like path-based routing; use Network Load Balancer (NLB) for ultra-low latency TCP/UDP at Layer 4 and static IP support.",
            "service": "Elastic Load Balancing",
            "url": "https://docs.aws.amazon.com/elasticloadbalancing/latest/userguide/what-is-load-balancing.html"
        },
        {
            "title": "EC2 Auto Scaling",
            "content": "Amazon EC2 Auto Scaling helps you maintain application availability and automatically adds or removes EC2 instances according to conditions you define.",
            "service": "EC2",
            "url": "https://docs.aws.amazon.com/autoscaling/"
        },
        {
            "title": "AWS Lambda Pricing Model",
            "content": "With AWS Lambda, you pay only for what you use. You are charged based on the number of requests for your functions and the duration of code execution.",
            "service": "Lambda",
            "url": "https://aws.amazon.com/lambda/pricing/"
        },
        {
            "title": "S3 Storage Classes",
            "content": "Amazon S3 offers a range of storage classes designed for different use cases including S3 Standard, S3 Intelligent-Tiering, S3 Glacier, and more.",
            "service": "S3",
            "url": "https://docs.aws.amazon.com/s3/storage-classes/"
        },
        {
            "title": "RDS Database Instances",
            "content": "Amazon RDS makes it easy to set up, operate, and scale a relational database in the cloud. It provides cost-efficient and resizable capacity.",
            "service": "RDS",
            "url": "https://docs.aws.amazon.com/rds/"
        },
        {
            "title": "VPC Networking Basics",
            "content": "Amazon Virtual Private Cloud (VPC) lets you provision a logically isolated section of the AWS Cloud where you can launch AWS resources in a virtual network.",
            "service": "VPC",
            "url": "https://docs.aws.amazon.com/vpc/"
        },
        {
            "title": "CloudWatch Monitoring",
            "content": "Amazon CloudWatch is a monitoring service for AWS cloud resources and applications. Collect and track metrics, collect and monitor log files, and set alarms.",
            "service": "CloudWatch",
            "url": "https://docs.aws.amazon.com/cloudwatch/"
        },
        {
            "title": "IAM Security Best Practices",
            "content": "AWS Identity and Access Management (IAM) enables you to securely control access to AWS services and resources. Use MFA, rotate credentials regularly.",
            "service": "IAM",
            "url": "https://docs.aws.amazon.com/iam/best-practices/"
        }
    ]


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
