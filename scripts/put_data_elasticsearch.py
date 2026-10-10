from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from pathlib import Path
import os
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / "docker" / ".env")

# Connection configuration
ES_HOST = os.getenv("ELASTIC_URL", "http://localhost:9200")
ES_USER = os.getenv("ELASTIC_USERNAME", "elastic")
ES_PASS = os.getenv("ELASTIC_PASSWORD")

if not ES_PASS:
    raise SystemExit("ELASTIC_PASSWORD not defined in .env")

es = Elasticsearch(
    ES_HOST,
    http_auth=(ES_USER, ES_PASS)
)

# Index configuration
INDEX_NAME = "sample-products"
NUM_DOCUMENTS = 100

# Sample data generators
CATEGORIES = ["Electronics", "Books", "Clothing", "Home & Garden", "Sports", "Toys", "Food & Beverages"]
BRANDS = ["BrandA", "BrandB", "BrandC", "BrandD", "BrandE", "BrandF"]
STATUSES = ["available", "out_of_stock", "discontinued"]

def generate_product(doc_id):
    """Generate a sample product document"""
    base_date = datetime.now() - timedelta(days=random.randint(0, 365))
    
    return {
        "_index": INDEX_NAME,
        "_id": f"product_{doc_id}",
        "_source": {
            "product_id": f"PRD-{doc_id:05d}",
            "name": f"Product {doc_id}",
            "description": f"This is a sample description for product {doc_id}",
            "category": random.choice(CATEGORIES),
            "brand": random.choice(BRANDS),
            "price": round(random.uniform(9.99, 999.99), 2),
            "stock_quantity": random.randint(0, 500),
            "status": random.choice(STATUSES),
            "rating": round(random.uniform(1.0, 5.0), 1),
            "reviews_count": random.randint(0, 1000),
            "created_at": base_date.isoformat(),
            "updated_at": (base_date + timedelta(days=random.randint(0, 30))).isoformat(),
            "tags": random.sample(["new", "sale", "featured", "bestseller", "eco-friendly"], k=random.randint(0, 3))
        }
    }

try:
    # Check if index exists and reset it (dummy data is always safe to recreate)
    if es.indices.exists(index=INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)
        print(f"Index '{INDEX_NAME}' already existed and was deleted for a clean reload.")
    
    # Create index with mapping
    mapping = {
        "mappings": {
            "properties": {
                "product_id": {"type": "keyword"},
                "name": {"type": "text"},
                "description": {"type": "text"},
                "category": {"type": "keyword"},
                "brand": {"type": "keyword"},
                "price": {"type": "float"},
                "stock_quantity": {"type": "integer"},
                "status": {"type": "keyword"},
                "rating": {"type": "float"},
                "reviews_count": {"type": "integer"},
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"},
                "tags": {"type": "keyword"}
            }
        },
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        }
    }
    
    es.indices.create(index=INDEX_NAME, body=mapping)
    print(f"Created index '{INDEX_NAME}' with mapping")
    
    # Generate documents
    documents = [generate_product(i + 1) for i in range(NUM_DOCUMENTS)]
    
    # Bulk insert
    success, failed = bulk(es, documents, raise_on_error=False)
    
    print(f"\nBulk insert completed:")
    print(f"  - Successfully indexed: {success} documents")
    if failed:
        print(f"  - Failed: {len(failed)} documents")
    
    # Refresh index to make documents searchable
    es.indices.refresh(index=INDEX_NAME)
    
    # Get index stats
    stats = es.cat.indices(index=INDEX_NAME, format="json", bytes="b")[0]
    size_mb = int(stats['store.size']) / (1024 * 1024)
    
    print(f"\nIndex Statistics:")
    print(f"  - Index: {INDEX_NAME}")
    print(f"  - Documents: {stats['docs.count']}")
    print(f"  - Size: {size_mb:.2f} MB")
    print(f"  - Health: {stats['health']}")
    print(f"  - Status: {stats['status']}")
    
    # Sample query
    print(f"\nSample Query (first 5 documents):")
    result = es.search(index=INDEX_NAME, body={"query": {"match_all": {}}, "size": 5})
    for hit in result['hits']['hits']:
        doc = hit['_source']
        print(f"  - {doc['product_id']}: {doc['name']} - ${doc['price']} ({doc['category']})")
    
    print(f"\nIndex '{INDEX_NAME}' ready for testing!")
    print(f"  Access in Kibana: http://localhost:5601/app/discover")

except Exception as e:
    print(f"Error creating index: {e}")
    import traceback
    traceback.print_exc()