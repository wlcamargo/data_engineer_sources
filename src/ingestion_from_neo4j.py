import json
from datetime import datetime
from neo4j import GraphDatabase
from functions.s3_utils import upload_to_s3

# Config Neo4j
uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "test"))

# Aqui assumo que essa função JÁ EXISTE em outro módulo seu
# from your_module import upload_to_s3


def get_graph(tx):
    query = """
    MATCH (s:Stack)-[:CONTAINS]->(c:Container)
    OPTIONAL MATCH (c)-[r:DEPENDS_ON]->(d:Container)
    RETURN s.name AS stack,
           c.name AS container,
           c.image AS image,
           collect(DISTINCT d.name) AS depends_on
    """
    result = tx.run(query)
    data = []
    for record in result:
        data.append({
            "stack": record["stack"],
            "container": record["container"],
            "image": record["image"],
            "depends_on": record["depends_on"],
        })
    return data


def main():
    with driver.session() as session:
        graph_data = session.read_transaction(get_graph)

    # Monta nome do arquivo e JSON
    key = "neo4j_containers"
    filename = f"{key}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.json"

    # graph_data é lista de dicts; se quiser identado no arquivo,
    # ainda pode mandar indentado ou “flat”
    data_json = json.dumps(graph_data)

    # Envia para MinIO (S3-compatible)
    upload_to_s3(filename, data_json, source="neo4j")

    print(f"Saved message to MinIO bucket as {filename}")

    driver.close()


if __name__ == "__main__":
    main()
