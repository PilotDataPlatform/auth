# Auth Service

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg?style=for-the-badge)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.9](https://img.shields.io/badge/python-3.9-green?style=for-the-badge)](https://www.python.org/)
![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/pilotdataplatform/auth/Run%20Tests/develop?style=for-the-badge)

Manages user related data as well as authentication and permissions. Connects to Keycloak and optionally AD or OpenLDAP

## Getting Started

### Prerequisites

This project is using [Poetry](https://python-poetry.org/docs/#installation) to handle the dependencies. Installtion instruction for poetry can be found at https://python-poetry.org/docs/#installation

### Installation & Quick Start


1. Clone the project.

       git clone https://github.com/PilotDataPlatform/auth.git

2. Install dependencies.

       poetry install
      
3. Add environment variables into `.env`. Use `.env.schema` as a reference.


4. Run setup scripts for postgres
    - [Create DB](https://github.com/PilotDataPlatform/auth/blob/develop/migrations/scripts/create_db.sql)
    - [Create Schemas](https://github.com/PilotDataPlatform/auth/blob/develop/migrations/scripts/create_schema.sql)

6. Run migration using alembic.

       poetry run alembic upgrade head
       
7. Run SQL script to populate casbin permissions
    - [Casbin Script](https://github.com/PilotDataPlatform/auth/blob/develop/migrations/scripts/create_schema.sql)

8. Run application.

       poetry run python run.py


### Startup using Docker

This project can also be started using [Docker](https://www.docker.com/get-started/).

1. To build and start the service within the Docker container, run:

       docker compose up

2. Migrations should run automatically after the previous step. They can also be manually triggered:

       docker compose run --rm alembic upgrade head

## Resources

* [Pilot Platform API Documentation](https://pilotdataplatform.github.io/api-docs/)
* [Pilot Platform Helm Charts](https://github.com/PilotDataPlatform/helm-charts/)

## Contribution

You can contribute the project in following ways:

* Report a bug.
* Suggest a feature.
* Open a pull request for fixing issues or adding functionality. Please consider
  using [pre-commit](https://pre-commit.com) in this case.
