# Angel Cloud Auth Bridge

A Flask-based authentication bridge for Angel Cloud. This service proxies authentication requests to the Angel Cloud API, handling API key authentication on behalf of the client.

## Installation

To install the project and its dependencies, navigate to the project's root directory and run:

```bash
pip install -e .
```

## Usage

### Web API

To run the web server, first create a `.env` file in the root of the project with the following content:

```
ANGEL_CLOUD_API_KEY=your_api_key
ANGEL_CLOUD_BASE_URL=https://api.angel-cloud.dev
```

Then, run the following command:

```bash
python api.py
```

The API will be available at `http://127.0.0.1:3005`.

### Endpoints

#### POST /auth/token

This endpoint proxies the request to the Angel Cloud `/auth/token` endpoint.

**Request Body:**

```json
{
    "username": "your_username",
    "password": "your_password"
}
```

**Response:**

The response from the Angel Cloud API is forwarded to the client.

#### POST /auth/validate

This endpoint proxies the request to the Angel Cloud `/auth/validate` endpoint.

**Request Body:**

```json
{
    "token": "your_token"
}
```

**Response:**

The response from the Angel Cloud API is forwarded to the client.
