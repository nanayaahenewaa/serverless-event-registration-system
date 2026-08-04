# DynamoDB Data Model

## Access Patterns
1. Register for an event → write a registration
2. List all events → read all events
3. View registrations by email → query registrations for a given email
4. Cancel a registration by ID → update/delete a specific registration

## Table 1: Events

| Attribute | Type | Role |
|---|---|---|
| eventId | String (UUID) | Partition key |
| eventName | String | attribute |
| eventDate | String (ISO 8601) | attribute |
| capacity | Number | attribute |
| registeredCount | Number | attribute |
| status | String (available/limited/full) | attribute |
| createdAt | String (ISO 8601) | attribute |

## Table 2: Registrations

| Attribute | Type | Role |
|---|---|---|
| registrationId | String (UUID) | Partition key |
| email | String | GSI partition key (EmailIndex) — enables `GET /registrations/{email}` |
| eventId | String | attribute (references Events table) |
| registeredAt | String (ISO 8601) | attribute |
| status | String (confirmed/cancelled) | attribute |

## Why the EmailIndex GSI

DynamoDB can only efficiently query by partition key. Registrations are stored
by `registrationId`, but the API needs to look them up by `email`
(`GET /registrations/{email}`). Without a GSI, this would require a full
table `scan()` with a filter — which reads every item in the table and
discards non-matches, an anti-pattern that doesn't scale. The `EmailIndex`
GSI gives `email` its own partition key, so lookups by email are a direct,
efficient `query()` instead.