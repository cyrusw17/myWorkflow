# Phase 6 — Database Schema

> **Status:** Complete · **Migrations:** `app/database/migrations/`

## ER diagram (v1 + v2-ready)

```mermaid
erDiagram
    users ||--o{ leads : assigns
    clients ||--o{ projects : has
    clients ||--o{ testimonials : has
    projects ||--o{ portfolio_items : showcases
    portfolio_items ||--o{ testimonials : optional

    leads {
        bigint id PK
        string name
        string phone
        string business_name
        string location
        string industry
        text message
        string source
        string status
        timestamps
    }

    portfolio_items {
        bigint id PK
        string slug UK
        string title
        string industry
        string tagline
        text challenge
        text approach
        text goals
        boolean is_concept
        boolean published
        json gallery
        int sort_order
        timestamps
    }

    clients {
        bigint id PK
        string name
        string email
        string phone
        timestamps
    }

    projects {
        bigint id PK
        bigint client_id FK
        string name
        string url
        string status
        timestamps
    }

    testimonials {
        bigint id PK
        bigint client_id FK
        bigint portfolio_item_id FK
        string quote
        string author
        boolean published
        timestamps
    }

    blog_posts {
        bigint id PK
        string slug UK
        string title
        text body
        boolean published
        timestamps
    }

    users {
        bigint id PK
        string email UK
        string password
        timestamps
    }
```

## v1 tables (implemented)

### `leads`

| Column | Type | Notes |
|--------|------|-------|
| id | bigint | PK |
| name | string(100) | required |
| phone | string(30) | required |
| business_name | string(150) | required |
| location | string(150) | city, state |
| industry | string(50) | enum-like |
| message | text | nullable |
| source | string(50) | default `contact_form` |
| status | string(30) | default `new` |
| ip_address | string(45) | nullable |
| created_at | timestamp | index |

Indexes: `status`, `created_at`.

### `portfolio_items`

| Column | Type | Notes |
|--------|------|-------|
| id | bigint | PK |
| slug | string | unique |
| title | string | |
| industry | string | |
| tagline | string | |
| challenge | text | |
| approach | text | |
| goals | text | |
| is_concept | boolean | default true |
| published | boolean | default true |
| gallery | json | image paths |
| sort_order | int | default 0 |

## v2 tables (migrations stubbed, not seeded)

- `clients`, `projects`, `testimonials`, `blog_posts`, `users` — create when admin ships.

## Seed data

`PortfolioItemSeeder`: Westside Auto Care (`westside-auto-care`).
