-- Initialize the database for Rehoboam project with pgvector support

-- Create the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create a basic users table (example)
-- CREATE TABLE IF NOT EXISTS users (
--     id SERIAL PRIMARY KEY,
--     username VARCHAR(255) UNIQUE NOT NULL,
--     email VARCHAR(255) UNIQUE NOT NULL,
--     created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
-- );

-- Example table with vector column for AI embeddings
-- CREATE TABLE IF NOT EXISTS embeddings (
--     id SERIAL PRIMARY KEY,
--     content TEXT NOT NULL,
--     embedding vector(1536), -- OpenAI embeddings are 1536 dimensions
--     created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
-- );

-- Create index for faster vector similarity searches
-- CREATE INDEX IF NOT EXISTS embeddings_embedding_idx ON embeddings 
-- USING ivfflat (embedding vector_cosine_ops);

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE rehoboam TO rehoboam;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO rehoboam;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO rehoboam;

-- Enable row level security if needed
-- ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- You can add more initialization scripts here
-- This file runs when the PostgreSQL container starts for the first time
