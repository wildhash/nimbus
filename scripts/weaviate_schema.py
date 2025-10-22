#!/usr/bin/env python3
"""
Initialize Weaviate schema for Nimbus Copilot.
Creates AWSDocs and CostPatterns collections.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.utils.weaviate_client import WeaviateClient


def create_aws_docs_schema():
    """Create schema for AWS documentation collection."""
    return {
        "class": "AWSDocs",
        "description": "AWS documentation chunks for RAG",
        "vectorizer": "text2vec-transformers",
        "moduleConfig": {
            "text2vec-transformers": {
                "poolingStrategy": "masked_mean"
            }
        },
        "properties": [
            {
                "name": "title",
                "dataType": ["text"],
                "description": "Document title",
                "moduleConfig": {
                    "text2vec-transformers": {
                        "skip": False,
                        "vectorizePropertyName": False
                    }
                }
            },
            {
                "name": "content",
                "dataType": ["text"],
                "description": "Document content",
                "moduleConfig": {
                    "text2vec-transformers": {
                        "skip": False,
                        "vectorizePropertyName": False
                    }
                }
            },
            {
                "name": "service",
                "dataType": ["text"],
                "description": "AWS service name",
                "moduleConfig": {
                    "text2vec-transformers": {
                        "skip": True
                    }
                }
            },
            {
                "name": "url",
                "dataType": ["text"],
                "description": "Documentation URL",
                "moduleConfig": {
                    "text2vec-transformers": {
                        "skip": True
                    }
                }
            },
            {
                "name": "category",
                "dataType": ["text"],
                "description": "Document category (compute, storage, networking, etc.)",
                "moduleConfig": {
                    "text2vec-transformers": {
                        "skip": True
                    }
                }
            }
        ]
    }


def create_cost_patterns_schema():
    """Create schema for cost patterns collection."""
    return {
        "class": "CostPatterns",
        "description": "Common AWS cost patterns and optimization strategies",
        "vectorizer": "text2vec-transformers",
        "moduleConfig": {
            "text2vec-transformers": {
                "poolingStrategy": "masked_mean"
            }
        },
        "properties": [
            {
                "name": "pattern_name",
                "dataType": ["text"],
                "description": "Name of the cost pattern"
            },
            {
                "name": "description",
                "dataType": ["text"],
                "description": "Detailed description of the pattern"
            },
            {
                "name": "services",
                "dataType": ["text[]"],
                "description": "AWS services involved"
            },
            {
                "name": "optimization_strategy",
                "dataType": ["text"],
                "description": "Recommended optimization approach"
            },
            {
                "name": "estimated_savings",
                "dataType": ["text"],
                "description": "Typical savings range"
            }
        ]
    }


def main():
    """Initialize Weaviate schema."""
    print("=" * 60)
    print("Nimbus Copilot - Weaviate Schema Initialization")
    print("=" * 60)
    
    # Initialize client
    print("\n1. Connecting to Weaviate...")
    client = WeaviateClient()
    
    if not client.is_available():
        print("❌ Weaviate is not available.")
        print("\nOptions:")
        print("  1. Start local Weaviate: docker run -d -p 8080:8080 semitechnologies/weaviate:latest")
        print("  2. Use Weaviate Cloud Services")
        print("  3. App will use mock data if Weaviate is unavailable")
        return 1
    
    print("✓ Connected to Weaviate")
    
    # Create AWSDocs schema
    print("\n2. Creating AWSDocs collection...")
    try:
        schema = create_aws_docs_schema()
        client.create_schema("AWSDocs", schema)
        print("✓ AWSDocs collection created")
    except Exception as e:
        print(f"⚠ AWSDocs: {e}")
    
    # Create CostPatterns schema
    print("\n3. Creating CostPatterns collection...")
    try:
        schema = create_cost_patterns_schema()
        client.create_schema("CostPatterns", schema)
        print("✓ CostPatterns collection created")
    except Exception as e:
        print(f"⚠ CostPatterns: {e}")
    
    print("\n" + "=" * 60)
    print("Schema initialization complete!")
    print("=" * 60)
    print("\nNext step: Run 'python scripts/seed_min_docs.py' to seed data")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
