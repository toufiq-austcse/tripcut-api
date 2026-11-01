# Supabase signs access tokens with asymmetric JWT signing keys (published at the JWKS URL).
JWT_ALGORITHMS = ["ES256", "RS256"]
JWT_AUDIENCE = "authenticated"
JWKS_PATH = "/auth/v1/.well-known/jwks.json"
ISSUER_PATH = "/auth/v1"
JWKS_CACHE_SECONDS = 600
