# Event Registration & Ticketing System

![Test](https://github.com/nanayaahenewaa/serverless-event-registration-system/actions/workflows/test.yml/badge.svg)
![Deploy](https://github.com/nanayaahenewaa/serverless-event-registration-system/actions/workflows/deploy.yml/badge.svg)

A serverless REST API replacing manual (Forms + Excel) event registration,
built on AWS Lambda, API Gateway, and DynamoDB.

## Status
🚧 In development — Phase 1: Infrastructure Foundation

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

## API Reference

### POST /register
Registers an email for an event.
**Body:** `{ "eventId": "string", "email": "string" }`
**Responses:** 201 Created | 400 Validation error | 404 Event not found | 409 At capacity

### GET /events
Returns all events.
**Responses:** 200 OK

### GET /registrations/{email}
Returns all registrations for the given email.
**Responses:** 200 OK (empty array if none found) | 400 Invalid email

### DELETE /registration/{id}
Cancels (soft-deletes) a registration and frees event capacity.
**Responses:** 200 OK | 404 Not found | 409 Already cancelled

## Running Tests
\`\`\`bash
pip install -r requirements-dev.txt
python -m pytest tests/unit/ -v
\`\`\`

## Local Development
\`\`\`bash
sam build
sam local invoke <FunctionName> --event events/<event-file>.json --env-vars local-env.json
\`\`\`

## Project Status
- [x] Phase 1: Infrastructure Foundation
- [x] Phase 2: API Development
- [ ] Phase 3: CI/CD
- [ ] Phase 4: Monitoring & Security
- [ ] Phase 5: Deployment & Optimization

## CI/CD Pipeline

This project uses GitHub Actions for continuous integration and deployment.

- **`test.yml`** — runs on every push and pull request: lints code, validates the
  SAM template, and runs the full unit test suite.
- **`deploy.yml`** — runs on every merge to `main`: re-runs tests as a safety net,
  then deploys via `sam deploy` to the `dev` stage.

Authentication to AWS uses **OIDC federation** — GitHub Actions assumes a scoped
IAM role (`github-actions-event-ticketing-deploy`) for the duration of each
workflow run. No long-lived AWS credentials are stored in this repository.

See [docs/oidc-debugging-notes.md](docs/oidc-debugging-notes.md) for a real
debugging writeup from setting this up.

### Branching Strategy
- `main` is protected: pull requests required, status checks must pass.
- Feature work happens on `feature/<name>` branches, merged via reviewed PRs.

## Project Status
- [x] Phase 1: Infrastructure Foundation
- [x] Phase 2: API Development
- [x] Phase 3: Automation & CI/CD
- [ ] Phase 4: Monitoring & Security
- [ ] Phase 5: Deployment & Optimization


## Monitoring & Alarms

CloudWatch alarms are configured for:
- Per-function error rate > 5% (Lambda `Errors`/`Invocations` ratio)
- API Gateway 5xx rate > 5%
- Lambda p99 duration approaching timeout
- DynamoDB throttling on the Registrations table

All alarms notify an SNS topic subscribed by email. Custom application metrics
(`SuccessfulRegistration`, `FailedRegistration`) are emitted via CloudWatch
Embedded Metric Format, visible under the `EventTicketingSystem` custom
namespace and on the included CloudWatch dashboard
(`event-ticketing-dev`).

## Security

- **IAM:** every Lambda execution role is scoped via AWS SAM policy templates
  to only the specific DynamoDB table/SNS topic actions it needs — see
  [docs/iam-audit.md](docs/iam-audit.md) for the verified audit.
- **Throttling:** API Gateway is rate-limited (10 req/s sustained, 20 burst)
  to protect against abuse and cost overrun on this public, unauthenticated API.
- **Input validation:** all input is validated and sanitized (type, length,
  format, request body size) before touching the database — see
  `src/common/validation.py`.
- **Cost control:** an AWS Budget (defined as code in `template.yaml`) alerts
  by email at 80% of actual spend and 100% of forecasted spend, capped at $5/month.
- **Optional confirmation notifications:** successful registrations trigger
  an SNS notification to an internal/admin topic — see the design note in
  the code for why this differs from per-registrant transactional email.

## Project Status
- [x] Phase 1: Infrastructure Foundation
- [x] Phase 2: API Development
- [x] Phase 3: Automation & CI/CD
- [x] Phase 4: Monitoring & Security
- [ ] Phase 5: Deployment & Optimization

## Cost

This project has operated entirely within AWS Free Tier throughout
development, across two full environments (dev and prod). As of the latest
check: month-to-date cost $0.00, forecasted monthly cost ~$0.05, and 0 of 12
active Free Tier service offerings at or above their usage limits.
