CREATE TABLE users (

    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    auth_user_id UUID UNIQUE,

    name VARCHAR(150) NOT NULL,

    email VARCHAR(255) NOT NULL UNIQUE,

    role VARCHAR(50) NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()

);