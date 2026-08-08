# Event Registration & Ticketing System

![Test](https://github.com/nanayaahenewaa/serverless-event-registration-system/actions/workflows/test.yml/badge.svg)
![Deploy](https://github.com/nanayaahenewaa/serverless-event-registration-system/actions/workflows/deploy.yml/badge.svg)

A serverless REST API replacing manual (Microsoft Forms + Excel) event
registration workflows, built on AWS Lambda, API Gateway, and DynamoDB,
with full CI/CD, monitoring, multi-stage deployment, and a live frontend.

## Live Demo
- Frontend: https://events.cloudastra.online
- API: https://7m5e7ocgj9.execute-api.us-east-1.amazonaws.com/prod

## Architecture
v+------------------+
            |      Client      |
            | Browser / Postman|
            +---------+--------+
                      |
          +-----------+-----------+
          |                       |
          v                       v
+------------------+    +------------------+
|   CloudFront      |    |   API Gateway    |
| (HTTPS + CDN)     |    +---------+--------+
+---------+---------+              |
          |                        v
          v              +------------------+
+------------------+     |   AWS Lambda     |
|   S3 (Frontend)  |     |  Business Logic  |
+------------------+     +---------+--------+
                                    |
                      +-------------+-------------+
                      |                           |
                      v                           v
            +------------------+       +------------------+
            |    DynamoDB      |       |   CloudWatch      |
            | Events &         |       | Logs, Alarms,     |
            | Registrations    |       | Dashboard         |
            +------------------+       +------------------+

## Why These Design Decisions

- **Serverless over always-on servers** — pay only for actual usage, zero
  idle cost. This project has operated within AWS Free Tier throughout
  development, across two full environments (dev and prod).
- **Two DynamoDB tables with a GSI, not single-table design** — clearer
  for a reviewer to follow, matches the brief's "Events & Registrations"
  framing. The `EmailIndex` GSI on Registrations avoids full table scans
  for email lookups.
- **Conditional writes for capacity enforcement** — prevents race
  conditions under concurrent registration requests without external locking.
- **Soft-delete on cancellation** — preserves an audit trail rather than
  destroying registration history.
- **OIDC over static AWS keys in CI/CD** — no long-lived credentials
  stored in GitHub. See [docs/oidc-debugging-notes.md](docs/oidc-debugging-notes.md)
  for a real debugging writeup on setting this up.
- **CloudWatch EMF over direct PutMetricData calls** — custom metrics with
  zero extra API calls or IAM permissions.

## Tech Stack

AWS Lambda (Python 3.12) · API Gateway · DynamoDB · CloudWatch · SNS ·
AWS Budgets · S3 · CloudFront · Route 53 · ACM · AWS SAM (IaC) ·
GitHub Actions (CI/CD, OIDC) · pytest + moto (testing) · Vanilla HTML/CSS/JS (frontend)

## Prerequisites
- AWS Account with configured CLI profile
- AWS SAM CLI
- Python 3.12
- Docker (for local testing)

## Getting Started

```bash
git clone <repo-url>
cd serverless-event-registration-system
pip install -r requirements-dev.txt
sam build
sam deploy --guided
```

## Local Development

```bash
sam build
sam local invoke <FunctionName> --event events/<event-file>.json --env-vars local-env.json
```

## API Reference

### POST /register
Registers an email for an event.
**Body:** `{ "eventId": "string", "email": "string" }`
**Responses:** 201 Created | 400 Validation error | 404 Event not found | 409 At capacity | 413 Body too large

### GET /events
Returns all events.
**Responses:** 200 OK

### GET /registrations/{email}
Returns all registrations for the given email.
**Responses:** 200 OK (empty array if none found) | 400 Invalid email

### DELETE /registration/{id}
Cancels (soft-deletes) a registration and frees event capacity.
**Responses:** 200 OK | 404 Not found | 409 Already cancelled

## Data Model
See [docs/data-model.md](docs/data-model.md) for full table schema and design rationale.

## Testing

```bash
pip install -r requirements-dev.txt
python -m pytest tests/unit/ -v
```

13 unit tests covering happy paths, validation failures, capacity limits, and
not-found cases across all 4 endpoints, using `moto` to mock DynamoDB — fully
offline, no AWS credentials required.

## CI/CD Pipeline

- **`test.yml`** — runs on every push and pull request: lints code, validates
  the SAM template, and runs the full unit test suite.
- **`deploy.yml`** — deploys to `dev` automatically on merge to `main`;
  deploys to `prod` only after manual approval via a GitHub Environment
  protection rule.

Authentication to AWS uses **OIDC federation** — GitHub Actions assumes a
scoped IAM role (`github-actions-event-ticketing-deploy`) for the duration
of each workflow run. No long-lived AWS credentials are stored in this
repository. See [docs/oidc-debugging-notes.md](docs/oidc-debugging-notes.md)
for a real debugging writeup from setting this up.

### Branching Strategy
- `main` is protected: pull requests required, status checks must pass.
- Feature work happens on `feature/<name>` branches, merged via reviewed PRs.

## Monitoring & Alarms

CloudWatch alarms are configured for:
- Per-function error rate > 5% (Lambda `Errors`/`Invocations` ratio)
- API Gateway 5xx rate > 5%
- Lambda p99 duration approaching timeout
- DynamoDB throttling on the Registrations table

All alarms notify an SNS topic subscribed by email. Custom application
metrics (`SuccessfulRegistration`, `FailedRegistration`) are emitted via
CloudWatch Embedded Metric Format, visible under the `EventTicketingSystem`
custom namespace and on the included CloudWatch dashboard.

## Security

- **IAM** — every Lambda execution role is scoped via AWS SAM policy
  templates to only the specific DynamoDB table/SNS topic actions it
  needs — see [docs/iam-audit.md](docs/iam-audit.md) for the verified audit.
- **Throttling** — API Gateway is rate-limited to protect against abuse and
  cost overrun on this public, unauthenticated API.
- **Input validation** — all input is validated and sanitized (type, length,
  format, request body size) before touching the database — see
  `src/common/validation.py`.
- **Cost control** — an AWS Budget (defined as code in `template.yaml`)
  alerts by email at 80% of actual spend and 100% of forecasted spend.
- **Optional confirmation notifications** — successful registrations
  trigger an SNS notification to an internal/admin topic — see the design
  note in the code for why this differs from per-registrant transactional email.

## Cost

This project has operated entirely within AWS Free Tier throughout
development, across two full environments (dev and prod). Verified: 0 of 12
active Free Tier service offerings at or above their usage limits.
Month-to-date cost: $0.00. Forecasted monthly cost: ~$0.05.

## Future Enhancements

- API Gateway request-model validation (deferred in favor of Lambda-layer
  validation, given added CloudFormation complexity for this project's scale)
- Cognito authentication (would require restructuring the data model around
  authenticated user identity rather than free-text email — a meaningful v2
  direction, not a small bolt-on)
- Multi-region deployment for disaster recovery

## Project Status

- [x] Phase 1: Infrastructure Foundation
- [x] Phase 2: API Development
- [x] Phase 3: Automation & CI/CD
- [x] Phase 4: Monitoring & Security
- [x] Phase 5: Deployment & Optimization 
