# Virtuoso Docker

## Installation
1. Download project to your machine: `git clone https://github.com/f-maury/virtuoso_docker.git`
2. Go to repository: `cd virtuoso_docker`
3. Install Docker-compose project: `sudo docker-compose up -d`
4. Create a Docker network for the container: `sudo docker network connect makaao_shared_net nginx`
5. Acces the Virtuoso instance's Conductor interface (default link: `https://YourDomainName/virtuoso/conductor`)
6. Login using default DBA credentials, username :`dba`, password: `dba`
7. In Conductor, go to "System Admin" > "Security" > click the "edit" button in the "dba" row, then enter a new password and save
8. In Conductor, go to "System Amdin" > "Packages" > on the "fct row, click install and then proceed, if the package is not already installed
9. In Conductor, go to "Linked Data" > "Quad Store Upload" > choose your .rdf file, and an URI for the graph (default settings work with `http://YourDomainName/kg/`)

You now have a Virtuoso instance running inside a Docker container, you can query your knowledge graph using the Virtuoso instance's SPARQL endpoint.

## Uninstall
1. To stop Docker container: `sudo docker stop virtuoso`
2. To uninstall Docker-compose project: `sudo docker-compose down`
  
## Access:
- Conductor UI: `https://YourDomainName/virtuoso/conductor`
- SPARQL UI: `https://YourDomainName/virtuoso/sparql`
- iSQL console inside the Virtuoso docker container (named `virtuoso`): `sudo docker exec -it virtuoso isql 1111 dba YourDBAPassword`
- Facet browser: `https://YourDomainName/fct/`
