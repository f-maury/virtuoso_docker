# Virtuoso Docker
Files in this repository are from OpenLink Virtuoso open-source edition, which is under GPL license. They are gathered in this repository, unaltered, for the sake of convenience only, in order to offer an easy Docker Compose deployment.
## Installation
1. ```bash
   git clone https://gitlab.com/Fabien-Maury/virtuoso_docker.git
   ```
   
2. ```bash
   cd virtuoso_docker
   ```
   
3. ```bash
    sudo docker-compose up -d
    ```

## Access
- Conductor UI: `localhost:8890/conductor`
- SPARQL UI: `localhost:8890/sparql`
- isql console: `docker exec -it virtuoso isql 1111 dba $DBA_PASSWORD`

## 1st connection
1. Go to Conductor UI
2. Log in with these credentials:
   - Account: dba
   - Password: dba
3. Go to "System Admin" > "User Accounts"
4. For account "dba", click "Edit"
5. Change password and save
   
## Data loading
1. Go to: Conductor UI, log in
2. Then, go to "Linked Data" > "Quad Store Upload"
3. Pick a local RDF file from your computer, and decide at which URI it will be available
