from fastapi.security import HTTPBearer

# auto_error=False so a missing token goes through our own 401 "unauthorized" error shape.
BEARER_SCHEME = HTTPBearer(auto_error=False, description="Supabase access token")
