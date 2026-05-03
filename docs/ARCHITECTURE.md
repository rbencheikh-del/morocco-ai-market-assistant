# Architecture

## Current Skeleton

- `src/app`: application shell and route-level composition.
- `src/components`: reusable interface components.
- `src/data`: temporary mock data for Moroccan market examples.
- `src/services`: product logic such as AI signal shaping.
- `src/api`: typed API contracts and mock client.
- `src/server`: planned backend route map.
- `src/types`: shared TypeScript domain types.
- `src/styles`: global UI styling.

## Suggested Production Stack

- Frontend: React with Vite or Next.js.
- Backend: Node.js API with a typed service layer.
- Database: PostgreSQL for users, portfolios, orders, audit logs, and acknowledgements.
- Jobs: scheduled market data ingestion and signal refresh tasks.
- AI: model gateway service with policy checks, prompt templates, output validation, and audit logging.
- Observability: structured logs, error tracking, model output review queue, and uptime monitoring.

## Data Flow

1. Market data ingestion normalizes Casablanca Stock Exchange data.
2. User portfolio and risk profile are loaded for the session.
3. The AI service receives bounded inputs and generates an educational signal.
4. Compliance checks add warnings, disclaimers, and audit metadata.
5. The UI displays recommendations as reviewable research, not execution instructions.
