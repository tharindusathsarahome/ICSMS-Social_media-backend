# SentiView iCSMS - Social Media Monitoring Part Backend API

## Overview

The SentiView iCSMS (Social Media Monitoring Part) Backend API is developed using FastAPI and MongoDB. This API serves as the backend for the social media monitoring component of the SentiView iCSMS application. It provides endpoints for managing users, social media data, and related functionalities.

## Features

- User authentication and authorization.
- CRUD operations for social media data.
- Integration with MongoDB for data storage.
- Fast and asynchronous API endpoints provided by FastAPI.

## Getting Started

### Prerequisites

- Python (3.7 or higher)
- MongoDB

### Installation

1. Clone the repository:

   ```bash
   git clone <repository_url>
   cd sentiview-icsms-backend
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

### Configuration

1. Create a `.env` file in the project root and configure the following variables:

   ```dotenv
   MONGODB_URI=<mongodb_uri>
   MONGODB_DB=<database_name>
   PAGE_ID=<page_id>
   ACCESS_TOKEN=<access_token>

   ```

   Replace `<mongodb_uri>` with the MongoDB connection URI and `<secret_key>` with a secure secret key for JWT token generation.

2. Update the MongoDB URI in the `app/core/config.py` file if necessary.

### Run the API

```bash
uvicorn app.main:app --reload
```

The API will be accessible at `http://127.0.0.1:8000`.

## API Documentation

Visit the API documentation at `http://127.0.0.1:8000/docs` for detailed information about available endpoints, request/response formats, and example usage.

## Testing

To run tests, use the following command:

```bash
pytest
```

## Docker Support

Docker support is included for containerization. Use the provided Dockerfile and docker-compose.yml file to build and run the application in a Docker container.

```bash
docker-compose up --build
```

## Contributing

Feel free to contribute to the project by opening issues or submitting pull requests. Follow the [Contributing Guidelines](CONTRIBUTING.md) for more details.

## License

This project is licensed under the [MIT License](LICENSE).