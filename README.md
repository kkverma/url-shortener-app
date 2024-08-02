# URL Shortening Service

This repository contains the code and configuration for a scalable URL Shortening Service using AWS services such as Lambda, API Gateway, DynamoDB, and ElastiCache. The service allows users to shorten URLs, redirect to the original URL, and optionally retrieve statistics for the shortened URLs.

## Architecture

- **API Gateway**: Handles HTTP requests and routes them to the appropriate Lambda functions.
- **Lambda Functions**: Implement the core logic for shortening URLs, redirecting, and retrieving statistics.
- **DynamoDB**: Stores the mapping of short URLs to long URLs.
- **ElastiCache (Redis)**: Caches the URL mappings to improve performance.

## Project Structure

- `assets/lambda/`: Contains the Lambda function code.
  - `shorten_lambda.py`: Handles URL shortening requests.
  - `redirect_lambda.py`: Handles redirection requests.
  - `stats_lambda.py`: Handles statistics retrieval requests.
- `url_shortener_app/`: Contains the AWS CDK stack definitions.
  - `url_shortener_app_stack.py`: Defines the infrastructure and resources using AWS CDK.

## Prerequisites

- AWS Account
- AWS CLI configured
- AWS CDK installed (`npm install -g aws-cdk`)
- Python 3.9+
- Node.js 12+

## Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/your-username/url-shortening-service.git
   cd url-shortening-service

2. **Install Dependencies**

    ```bash
    pip install -r requirements.txt

3. **Bootstrap the CDK (if not already done)**

    ```bash
    cdk bootstrap

4. **Deploy the Stack**

    ```bash
    cdk deploy

## Lambda Functions

### Shorten URL Function
Handles POST requests to shorten a URL.

* Endpoint: /shorten
* Method: POST
* Request Body:
    ```json
    {
    "longUrl": "https://example.com/your-long-url"
    }
    ```
* Response Body:
    ```json
    {
    "shortUrl": "abc123"
    }
    ```

### Redirect Function
Handles GET requests to redirect to the original URL.

* Endpoint: /{shortUrl}
* Method: GET
* Response: 301 Redirect to the original URL

### Stats Function (Optional)
Handles GET requests to retrieve statistics for a shortened URL.

* Endpoint: /{shortUrl}/stats
* Method: GET
* Response Body:
    ```json
    {
    "longUrl": "https://example.com/your-long-url",
    "accessCount": 10,
    "createdAt": "1609459200"
    }
    ```

## Cleanup
To delete the deployed stack:

    ```bash
    cdk destroy

## Contributing
Contributions are welcome! Please submit a pull request or open an issue to discuss your changes.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
