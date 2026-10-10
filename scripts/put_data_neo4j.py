import docker
from neo4j import GraphDatabase
import subprocess

client = docker.from_env()

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "test"))


def create_stack(tx, stack_name):
    tx.run("MERGE (s:Stack {name: $name})", name=stack_name)


def create_container(tx, container_name, image, stack_name):
    query = (
        "MERGE (c:Container {name: $name}) "
        "ON CREATE SET c.image = $image "
        "WITH c "
        "MERGE (s:Stack {name: $stack_name}) "
        "MERGE (s)-[:CONTAINS]->(c)"
    )
    tx.run(query, name=container_name, image=image, stack_name=stack_name)


def create_dependency(tx, src_container, dest_container):
    query = (
        "MATCH (a:Container {name: $src_name}), (b:Container {name: $dest_name}) "
        "MERGE (a)-[:DEPENDS_ON]->(b)"
    )
    tx.run(query, src_name=src_container, dest_name=dest_container)


with driver.session() as session:
    containers = client.containers.list()
    container_map = {}

    for container in containers:
        container_name = container.name
        tags = container.image.tags
        container_image = tags if tags else "unknown"

        stack_name = container.labels.get("com.docker.compose.project", "unknown")
        container_map.setdefault(stack_name, []).append(container_name)

        session.write_transaction(create_container, container_name, container_image, stack_name)

    for stack_name, containers_in_stack in container_map.items():
        if len(containers_in_stack) < 2:
            continue
        for i in range(len(containers_in_stack)):
            for j in range(i + 1, len(containers_in_stack)):
                src_container = containers_in_stack[i]
                dest_container = containers_in_stack[j]
                session.write_transaction(create_dependency, src_container, dest_container)

        print(f"Stack '{stack_name}' successfully exported to Neo4j with {len(containers_in_stack)} containers.")

driver.close()