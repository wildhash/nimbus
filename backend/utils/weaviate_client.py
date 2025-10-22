"""
Weaviate client for semantic search with hybrid search support.
"""
import os
from typing import List, Dict, Any, Optional

try:
    import weaviate
    from weaviate.classes.init import Auth
    from weaviate.classes.query import Filter, MetadataQuery
    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False


class WeaviateClient:
    """Client for Weaviate vector database with hybrid search."""
    
    def __init__(self):
        self.url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
        self.api_key = os.getenv("WEAVIATE_API_KEY")
        self.client = None
        
        if WEAVIATE_AVAILABLE:
            try:
                self._connect()
            except Exception as e:
                print(f"Warning: Could not connect to Weaviate: {e}")
    
    def _connect(self):
        """Connect to Weaviate instance."""
        try:
            if self.api_key:
                # For Weaviate Cloud
                self.client = weaviate.connect_to_wcs(
                    cluster_url=self.url,
                    auth_credentials=Auth.api_key(self.api_key)
                )
            else:
                # For local instance
                self.client = weaviate.connect_to_local(
                    host=self.url.replace("http://", "").replace("https://", "")
                )
            print(f"Connected to Weaviate at {self.url}")
        except Exception as e:
            # Try old client for backwards compatibility
            try:
                if self.api_key:
                    self.client = weaviate.Client(
                        url=self.url,
                        auth_client_secret=weaviate.AuthApiKey(api_key=self.api_key)
                    )
                else:
                    self.client = weaviate.Client(url=self.url)
                print(f"Connected to Weaviate (legacy) at {self.url}")
            except Exception as e2:
                print(f"Failed to connect: {e}, {e2}")
                self.client = None
    
    def is_available(self) -> bool:
        """Check if Weaviate client is available."""
        return self.client is not None
    
    def create_schema(self, collection_name: str, schema_config: Dict[str, Any]):
        """
        Create a collection schema in Weaviate.
        
        Args:
            collection_name: Name of the collection
            schema_config: Schema configuration dictionary
        """
        if not self.client:
            raise Exception("Weaviate client not available")
        
        try:
            # Check if schema exists
            try:
                schema = self.client.schema.get()
                collection_exists = any(
                    c.get("class") == collection_name 
                    for c in schema.get("classes", [])
                )
                
                if collection_exists:
                    print(f"Collection {collection_name} already exists")
                    return
            except:
                pass
            
            # Create schema
            self.client.schema.create_class(schema_config)
            print(f"Created collection: {collection_name}")
        except Exception as e:
            print(f"Error creating schema: {e}")
    
    def add_documents(
        self,
        collection_name: str,
        documents: List[Dict[str, Any]],
        batch_size: int = 100
    ):
        """
        Add documents to a collection.
        
        Args:
            collection_name: Name of the collection
            documents: List of document dictionaries
            batch_size: Batch size for insertion
        """
        if not self.client:
            raise Exception("Weaviate client not available")
        
        try:
            with self.client.batch as batch:
                batch.batch_size = batch_size
                for doc in documents:
                    batch.add_data_object(
                        data_object=doc,
                        class_name=collection_name
                    )
            print(f"Added {len(documents)} documents to {collection_name}")
        except Exception as e:
            print(f"Error adding documents: {e}")
    
    def hybrid_search(
        self,
        collection_name: str,
        query: str,
        limit: int = 5,
        alpha: float = 0.5,
        properties: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search (vector + keyword).
        
        Args:
            collection_name: Name of the collection
            query: Search query
            limit: Maximum number of results
            alpha: Balance between vector (1.0) and keyword (0.0) search
            properties: Properties to return
            
        Returns:
            List of matching documents
        """
        if not self.client:
            return self._get_mock_results(query, limit)
        
        try:
            # Try new client API
            if hasattr(self.client, 'collections'):
                collection = self.client.collections.get(collection_name)
                response = collection.query.hybrid(
                    query=query,
                    limit=limit,
                    alpha=alpha,
                    return_metadata=MetadataQuery(score=True)
                )
                
                results = []
                for item in response.objects:
                    results.append({
                        **item.properties,
                        "_score": item.metadata.score if item.metadata else None
                    })
                return results
            
            # Fallback to old API
            else:
                props = properties or ["title", "content", "service", "url"]
                result = (
                    self.client.query
                    .get(collection_name, props)
                    .with_hybrid(query=query, alpha=alpha)
                    .with_limit(limit)
                    .with_additional(["score"])
                    .do()
                )
                
                documents = []
                if result.get("data", {}).get("Get", {}).get(collection_name):
                    for item in result["data"]["Get"][collection_name]:
                        doc = {k: v for k, v in item.items() if k != "_additional"}
                        if "_additional" in item and "score" in item["_additional"]:
                            doc["_score"] = item["_additional"]["score"]
                        documents.append(doc)
                
                return documents
        
        except Exception as e:
            print(f"Hybrid search error: {e}")
            return self._get_mock_results(query, limit)
    
    def semantic_search(
        self,
        collection_name: str,
        query: str,
        limit: int = 5,
        properties: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic (vector) search only.
        
        Args:
            collection_name: Name of the collection
            query: Search query
            limit: Maximum number of results
            properties: Properties to return
            
        Returns:
            List of matching documents
        """
        if not self.client:
            return self._get_mock_results(query, limit)
        
        try:
            # Try new client API
            if hasattr(self.client, 'collections'):
                collection = self.client.collections.get(collection_name)
                response = collection.query.near_text(
                    query=query,
                    limit=limit,
                    return_metadata=MetadataQuery(distance=True)
                )
                
                results = []
                for item in response.objects:
                    results.append({
                        **item.properties,
                        "_distance": item.metadata.distance if item.metadata else None
                    })
                return results
            
            # Fallback to old API
            else:
                props = properties or ["title", "content", "service", "url"]
                result = (
                    self.client.query
                    .get(collection_name, props)
                    .with_near_text({"concepts": [query]})
                    .with_limit(limit)
                    .with_additional(["distance"])
                    .do()
                )
                
                documents = []
                if result.get("data", {}).get("Get", {}).get(collection_name):
                    for item in result["data"]["Get"][collection_name]:
                        doc = {k: v for k, v in item.items() if k != "_additional"}
                        if "_additional" in item and "distance" in item["_additional"]:
                            doc["_distance"] = item["_additional"]["distance"]
                        documents.append(doc)
                
                return documents
        
        except Exception as e:
            print(f"Semantic search error: {e}")
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
            },
            {
                "title": "AWS CloudFormation",
                "content": "AWS CloudFormation is a service that helps you model and set up your AWS resources. You create a template that describes all the AWS resources that you want.",
                "service": "CloudFormation",
                "url": "https://docs.aws.amazon.com/cloudformation/"
            },
            {
                "title": "AWS Lambda Pricing",
                "content": "AWS Lambda pricing is based on the number of requests and the duration of code execution. You are charged for requests and compute time.",
                "service": "Lambda",
                "url": "https://aws.amazon.com/lambda/pricing/"
            }
        ]
        
        return mock_docs[:limit]
    
    def close(self):
        """Close the Weaviate connection."""
        if self.client:
            try:
                self.client.close()
            except:
                pass
