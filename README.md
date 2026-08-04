# Event Registration & Ticketing System

A serverless REST API replacing manual (Forms + Excel) event registration,
built on AWS Lambda, API Gateway, and DynamoDB.

## Status
🚧 In development — Phase 1: Infrastructure Foundation

## Architecture
(diagram coming in Phase 1 completion)

## Tech Stack
- AWS Lambda (Python 3.12)
- Amazon API Gateway (REST)
- Amazon DynamoDB
- Amazon CloudWatch
- AWS SAM (Infrastructure as Code)
- GitHub Actions (CI/CD)

## Architecture
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


## Prerequisites
- AWS Account with configured CLI profile
- AWS SAM CLI
- Python 3.12
- Docker (for local testing)

## Infrastructure
This project's AWS infrastructure is fully defined as code in `template.yaml`
using AWS SAM. Deploy it yourself:

\`\`\`bash
sam build
sam deploy --guided
\`\`\`

## Data Model
See [docs/data-model.md](docs/data-model.md) for full table schema and design rationale.

## Project Status
- [x] Phase 1: Infrastructure Foundation
- [ ] Phase 2: API Development
- [ ] Phase 3: CI/CD
- [ ] Phase 4: Monitoring & Security
- [ ] Phase 5: Deployment & Optimization