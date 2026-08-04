# Architecture Overview

## Project Summary

This project is a serverless Task Management REST API built on AWS. It allows users to create, retrieve, update, and delete tasks through HTTP endpoints. The application uses managed AWS services, eliminating the need to manage servers.

---

## Architecture Components

| Component | Purpose |
|-----------|---------|
| Amazon API Gateway | Receives HTTP requests and exposes REST API endpoints |
| AWS Lambda | Executes the application logic |
| Amazon DynamoDB | Stores task data |
| IAM | Grants secure permissions between AWS services |
| CloudWatch | Collects logs and monitors Lambda execution |

---

## Request Flow

1. A client sends an HTTP request to the API Gateway.
2. API Gateway routes the request to the appropriate Lambda function.
3. Lambda validates the request and performs the required business logic.
4. Lambda reads from or writes to DynamoDB.
5. DynamoDB returns the requested data.
6. Lambda sends the response back through API Gateway to the client.
7. CloudWatch records logs and execution metrics throughout the process.

---

## Rough Architecture Diagram

```
                +------------------+
                |      Client      |
                | Postman / Browser|
                +---------+--------+
                          |
                          v
                +------------------+
                |  API Gateway     |
                +---------+--------+
                          |
                          v
                +------------------+
                |   AWS Lambda     |
                | Business Logic   |
                +---------+--------+
                          |
              +-----------+-----------+
              |                       |
              v                       v
      +---------------+      +----------------+
      | DynamoDB      |      | CloudWatch     |
      | Task Storage  |      | Logs & Metrics |
      +---------------+      +----------------+
```

---

## Design Decisions

- **Serverless architecture** reduces operational overhead.
- **API Gateway** provides a secure REST interface.
- **Lambda** automatically scales based on incoming requests.
- **DynamoDB** provides low-latency NoSQL storage.
- **CloudWatch** enables monitoring and troubleshooting.

---

## Benefits

- Scalable
- Cost-effective
- Highly available
- Fully managed
- Easy to extend with authentication or additional endpoints