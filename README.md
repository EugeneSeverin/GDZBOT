# GDZBot Project

This project sets up a development environment using Docker for the GDZBot application, which includes a PostgreSQL database. The environment is orchestrated with Docker Compose to simplify the management of services.

## Table of Contents

- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Introduction

The GDZBot project is an asynchronous Telegram bot designed to provide several functionalities, including:

- Conversing with ChatGPT for interactive AI-driven chat experiences.
- Managing user balances with easy-to-use commands.
- Offering a user panel for managing settings and viewing statistics.
- Providing real-time balance updates and usage information for users.

This bot leverages PostgreSQL as its database backend and utilizes Docker and Docker Compose to streamline setup and deployment.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- [Docker](https://www.docker.com/get-started) installed on your machine.
- [Docker Compose](https://docs.docker.com/compose/install/) installed on your machine.
- [Python](https://www.python.org/downloads/) installed on your machine.

## Installation

To set up the development environment, follow these steps:

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/gdzbot-project.git
    cd gdzbot-project
    ```

2. Build and start the Docker containers:

    ```bash
    docker-compose up --build
    ```

    This command will build the GDZBot service and start both the PostgreSQL and GDZBot containers.

3. Set up the Python environment and install dependencies:

    Create a virtual environment:

    ```bash
    python -m venv venv
    ```

    Activate the virtual environment:

    - On Windows:

      ```bash
      venv\Scripts\activate
      ```

    - On macOS and Linux:

      ```bash
      source venv/bin/activate
      ```

    Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

    Ensure you have a `requirements.txt` file in your project root with the following content:

    ```plaintext
    aiogram==3.2
    pymysql==1.1.0
    openai==1.3.7
    requests==2.31.0
    psycopg2==2.9.9
    ```

## Usage

The project consists of two main services:

- **PostgreSQL Database**: Accessible on port `5432`. The database is initialized with the following credentials:
  - **Database**: `DBName`
  - **User**: `rootUser`
  - **Password**: `rootPassword`

- **GDZBot**: The bot application service, which depends on the PostgreSQL service. You can find its files in the `./volumes/gdzbot/` directory. It is initially set to run the command `tail -f /dev/null` for debugging purposes. Modify the command as needed to start the bot service.

### Accessing the Services

- **PostgreSQL**: You can access the database using any PostgreSQL client on `localhost:5432`.

### Running GDZBot

To run GDZBot with the necessary environment variables, update the `command` section in the `docker-compose.yml` to start your application. For example, if your bot script is `main.py`, you can replace the `command`:

```yaml
command: python main.py
