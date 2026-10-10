from pymongo import MongoClient
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote_plus
import os
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / "docker" / ".env")


def connect_to_mongodb(username: str, password: str, host: str = "localhost", port: int = 27017):
    """
    Establish a connection to MongoDB using authentication.
    """
    uri = f"mongodb://{quote_plus(username)}:{quote_plus(password)}@{host}:{port}/?authSource=admin"
    client = MongoClient(uri)
    
    # Test connection
    client.admin.command("ping")
    print("Connected to MongoDB with authentication successfully.")
    
    return client


def create_database(client, database_name: str):
    """
    Create or access a database.
    """
    db = client[database_name]
    print(f"Database '{database_name}' is ready.")
    return db


def create_collection(db, collection_name: str):
    """
    Create or access a collection.
    """
    collection = db[collection_name]
    print(f"Collection '{collection_name}' is ready.")
    return collection


def insert_complaint(collection, branch: str, person_name: str, email: str, complaint_text: str):
    """
    Insert a new complaint into the collection.
    MongoDB automatically generates the complaint ID (_id).
    """
    complaint_document = {
        "branch": branch,
        "person_name": person_name,
        "email": email,
        "complaint_text": complaint_text,
        "created_at": datetime.now(timezone.utc)
    }

    result = collection.insert_one(complaint_document)
    print(f"Complaint inserted successfully with ID: {result.inserted_id}")


def main():
    """
    Main execution function.
    """
    username = os.getenv("MONGO_INITDB_ROOT_USERNAME", "chapolin")
    password = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
    if not password:
        raise SystemExit("MONGO_INITDB_ROOT_PASSWORD not defined in .env")
    database_name = "complaints_db"
    collection_name = "complaints"

    client = connect_to_mongodb(username, password)
    db = create_database(client, database_name)
    collection = create_collection(db, collection_name)

    # Example complaints in Portuguese
    insert_complaint(
        collection,
        branch="Filial São Paulo",
        person_name="João Silva",
        email="joao.silva@email.com",
        complaint_text="O atendimento foi muito demorado e não resolveram meu problema."
    )

    insert_complaint(
        collection,
        branch="Filial Rio de Janeiro",
        person_name="Maria Oliveira",
        email="maria.oliveira@email.com",
        complaint_text="Produto veio com defeito e não consegui trocar na loja."
    )

    client.close()
    print("Connection closed.")


if __name__ == "__main__":
    main()