# Dev environment

## Setup without Dev Containers

You will need to configure .env file with environment variables, please refer to `.env.example`.

```
pip install invoke
pip install -r requirements.txt
npm install -g tailwindcss
invoke run
```

This repo includes a Dev Containers setup in `.devcontainer/`

## Prerequisites

1. Docker Desktop (or Docker Engine)

2. One of the following:
    - VS Code with the Dev Containers extension
    - Dev Container CLI (part of the Dev Containers extension, can be installed separately): `npm install -g @devcontainers/cli`

## Working in terminal

Build and start the container:

```
devcontainer up
devcontainer exec uvx invoke run
```

**Pro tip:** you can use environment variables to override default host and port: `FLASK_RUN_HOST=0.0.0.0 FLASK_RUN_PORT=1337 devcontainer up`

## Working in VSCode

1. Open this repository in VS Code.
2. Run `Dev Containers: Reopen in Container` from the command palette.
3. Wait for the container to build. It runs `uv sync --group local` automatically.

## Run the app

```
uvx invoke run
```

The app listens on port 8000 (forwarded from the container).

## Services and environment

- App service: Python 3.12 container with Node and uv
- Database: Postgres 16 at `postgres://postgres:postgres@db:5432/ctf_mn`
- Environment variables are loaded from .devcontainer/.env and mapped into the container

# SQL. Update user fields

```
UPDATE "ctf_mn--user" u
SET
    solved_count = (
        SELECT COUNT(*)
        FROM "ctf_mn--submission" s
        WHERE s.user_id = u.id
        AND s.status = 'CORRECT'
    ),
    last_solved_at = (
        SELECT s.created_at
        FROM "ctf_mn--submission" s
        WHERE s.user_id = u.id
        AND s.status = 'CORRECT'
        ORDER BY s.created_at DESC
        LIMIT 1
    )
WHERE EXISTS (
    SELECT 1
    FROM "ctf_mn--submission" s
    WHERE s.user_id = u.id
    AND s.status = 'CORRECT'
);

UPDATE "ctf_mn--user" u
SET scores = (
    SELECT COALESCE(SUM(c.score), 0)
    FROM "ctf_mn--submission" s
    JOIN "ctf_mn--challenge" c ON s.challenge_id = c.id
    WHERE s.user_id = u.id AND s.status = 'CORRECT'
);
```

# SQL. Update challenge fields

```
WITH solved_counts AS (
    SELECT
        s.challenge_id,
        COUNT(*) AS solved_count
    FROM
        "ctf_mn--submission" s
    WHERE
        s.status = 'CORRECT'
    GROUP BY
        s.challenge_id
)
UPDATE "ctf_mn--challenge" c
SET
    solved_count = sc.solved_count,
    score = GREATEST(10, 1000 - sc.solved_count * (sc.solved_count - 1) / 2)
FROM
    solved_counts sc
WHERE
    c.id = sc.challenge_id;
```

# SQL. Find duplication

```
SELECT challenge_id, user_id, COUNT(*) AS count
FROM "ctf_mn--submission"
WHERE status = 'CORRECT'
GROUP BY user_id, challenge_id
HAVING COUNT(*) > 1;
```

# SQL. Changelog

```
SELECT '- '|| initcap(category) ||'. ['|| title ||'](https://ctf.mn/challenge/'|| id ||')'
FROM "ctf_mn--challenge"
ORDER BY id DESC LIMIT 100;
```

# SQL. Service URL change

```
UPDATE "ctf_mn--challenge"
SET content = REPLACE(content, 'nc 139.162.5.230 ', 'nc 139.59.230.119 ')
WHERE "content" LIKE '%nc 139.162.5.230 %';
```

# Routes

**Core**

- `/` — 100%
- `/scoreboard` — 100%
- `/activity` — 100%
- `/discord` — 100%
- `/user/<name>` — 100%
- `/author/<name>` — 100%

**Auth**

- `/register` — 88%
- `/login` — 74%
- `/logout` — 100%
- `/forgot-password/reset` — 0%

**Challenges**

- `/challenge` — 100%
- `/challenge/list` — 100%
- `/challenge/<int:challenge_id>` — 91%

**Contests**

- `/contest/<int:contest_id>` — 0%
- `/contest/<int:contest_id>/challenge` — 0%
- `/contest/<int:contest_id>/challenge/list` — 0%
- `/contest/<int:contest_id>/challenge/<int:challenge_id>` — 0%
- `/contest/<int:contest_id>/activity` — 0%

**API**

- `/api/contest-challenge` — 0%
- `/api/challenge` — 88%
