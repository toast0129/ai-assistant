-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- GitHub recommendations
CREATE TABLE github_items (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repo_id     TEXT UNIQUE NOT NULL,       -- e.g. "owner/repo"
    title       TEXT NOT NULL,
    url         TEXT NOT NULL,
    summary     TEXT,
    stars       INT,
    language    TEXT,
    topics      TEXT[],
    score       INT,                        -- Claude 評分 1-10
    embedding   vector(1536),              -- for dedup
    seen_at     TIMESTAMPTZ DEFAULT now(),
    created_at  TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX ON github_items USING hnsw (embedding vector_cosine_ops);

-- Email items
CREATE TABLE email_items (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id   TEXT UNIQUE NOT NULL,
    subject      TEXT,
    sender       TEXT,
    importance   INT,                       -- 1-5
    summary      TEXT,
    action_needed BOOLEAN DEFAULT false,
    raw_snippet  TEXT,
    received_at  TIMESTAMPTZ,
    created_at   TIMESTAMPTZ DEFAULT now()
);

-- YouTube recommendations
CREATE TABLE youtube_items (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id    TEXT UNIQUE NOT NULL,
    title       TEXT NOT NULL,
    channel     TEXT,
    url         TEXT NOT NULL,
    summary     TEXT,
    value_score INT,
    fit_score   INT,
    duration    TEXT,
    embedding   vector(1536),
    seen_at     TIMESTAMPTZ DEFAULT now(),
    created_at  TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX ON youtube_items USING hnsw (embedding vector_cosine_ops);

-- Feedback (回饋機制)
CREATE TABLE feedback (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    item_id     UUID NOT NULL,
    item_type   TEXT NOT NULL,              -- 'github'|'email'|'youtube'
    action      TEXT NOT NULL,             -- 'clicked'|'dismissed'|'saved'
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- Daily cost log
CREATE TABLE cost_log (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    module      TEXT NOT NULL,             -- 'github'|'email'|'youtube'
    tokens_in   INT,
    tokens_out  INT,
    cost_usd    NUMERIC(10,6),
    logged_at   TIMESTAMPTZ DEFAULT now()
);
