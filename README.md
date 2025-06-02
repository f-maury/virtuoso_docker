# Virtuoso Docker

## Installation
1. `git clone https://gitlab.com/Fabien-Maury/virtuoso_docker.git`
2. `cd virtuoso_docker`
3. Set DBA_password in `docker-compose.yml`
4. Place the data you want in a .rdf file, in `virtuoso_docker/data/`
5. `sudo docker-compose up -d`  

## Access:
- Conductor UI: `localhost:8890/conductor`
- SPARQL UI: `localhost:8890/sparql`
- isql console: `docker exec -it virtuoso isql 1111 dba $DBA_PASSWORD`