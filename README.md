# Setup Data Engineer

This project simulates a data engineering environment with multiple data sources, including:

- **Neo4j** - Graph Database
- **Elasticsearch** - Search and Analytics Engine
- **PostgreSQL** - Relational Database (AdventureWorks)
- **SQL Server** - Microsoft Relational Database
- **Kafka** - Distributed Event Streaming Platform
- **MongoDB** - NoSQL Document Database


## Architecture
![image](assets/sources.png)

## Prerequisites

- Docker 
  - Tutorial instalation: https://www.youtube.com/playlist?list=PLbPvnlmz6e_L_3Zw_fGtMcMY0eAOZnN-H


## Quick Start

### Clone the Repository

```bash
git clone wlcamargo/data_engineer_sources
cd data_engineer_sources
```

### Start All Services

```bash
cd docker/
docker-compose up -d
```

## Data Sources Configuration

### PostgreSQL AdventureWorks

- **Host:** localhost
- **Port:** 5435
- **Database:** Adventureworks
- **Username:** postgres
- **Password:** postgres

The AdventureWorks database comes pre-loaded with sample data.

### MongoDB

- **Host:** localhost
- **Port:** 27017
- **Username:** chapolin
- **Password:** mudar123
- **Auth Database:** admin
- **Connection String:** `mongodb://chapolin:mudar123@localhost:27017`

### SQL Server

- **Host:** localhost
- **Port:** 1435
- **Database:** master
- **Username:** sa
- **Password:** mudar@123

### Neo4j

- **Browser Interface:** http://localhost:7474
- **Bolt Protocol:** bolt://localhost:7687
- **Username:** neo4j
- **Password:** test

### Elasticsearch

- **URL:** http://localhost:9200
- **Username:** elastic
- **Password:** mudar@123
- **Cluster:** docker-cluster

### Kafka

- **Broker:** localhost:9092
- **Kafka UI:** http://localhost:9007
- **KSQLDB:** http://localhost:8088



## References

- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Elasticsearch Documentation](https://www.elastic.co/guide/)
- [Neo4j Documentation](https://neo4j.com/docs/)
- [SQL Server Documentation](https://docs.microsoft.com/en-us/sql/)

## 🧑🏼‍🚀 Developer
| Developer    | LinkedIn                                   | Email                        | Portfolio                              |
|--------------------|--------------------------------------------|------------------------------|----------------------------------------|

| Wallace Camargo    | [LinkedIn](https://www.linkedin.com/in/wallace-camargo-35b615171/) | wallacecpdg@gmail.com        | [Portfólio](https://wlcamargo.github.io/)   |