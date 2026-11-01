# Rollout: tripcut-api (SAN-51)

A person runs these steps. Nothing here was run by the agent.
Needs: `wrangler` (logged in to the Cloudflare account), `supabase` CLI, `modal` CLI (logged in), Python 3.12+.

```text
 [1 bucket] -> [2 CORS] -> [3 lifecycle] -> [4 R2 token] -> [5 Supabase keys + db push]
   -> [6 Modal secret] -> [7 modal deploy] -> [8 smoke test] -> [9 FE base URL]
```

## 1. R2 bucket
```bash
wrangler r2 bucket create tripcut-media
```

## 2. R2 CORS (browser PUTs only)
Edit `infra/r2/cors.json`: replace `https://REPLACE-WITH-WEB-ORIGIN` with the production web origin
(for example the Cloudflare Pages URL). Then:
```bash
wrangler r2 bucket cors set tripcut-media --file infra/r2/cors.json
wrangler r2 bucket cors list tripcut-media
```

## 3. R2 lifecycle (abort unfinished multipart uploads after 1 day)
```bash
wrangler r2 bucket lifecycle set tripcut-media --file infra/r2/lifecycle.json
wrangler r2 bucket lifecycle list tripcut-media
```
Object expiry (7 / 30 days) is SAN-58, not this step.

## 4. R2 API token
Cloudflare dashboard → R2 → Manage API tokens → **Object Read & Write**, limited to bucket `tripcut-media`.
Keep the Access Key ID, Secret Access Key and the account id.

## 5. Supabase
1. Dashboard → Authentication → Providers → Email: on, magic link on. Add the web origin and
   `http://localhost:5173` to the redirect URLs.
2. Dashboard → Project Settings → JWT Keys: make sure an **asymmetric signing key** (ES256 or RS256) is
   the current key. The API checks tokens against `https://<ref>.supabase.co/auth/v1/.well-known/jwks.json`;
   a project that still signs with the legacy HS256 secret has no key there and every call returns 401.
3. Push the schema (from `tripcut-api/`):
```bash
supabase link --project-ref <ref>
supabase db push
```
4. Copy the **session pooler** connection string (port 5432) for `SUPABASE_DB_URL`. It uses the `postgres` role,
   which owns the tables, so the API can write while RLS keeps browsers read-only.

Rollback: `psql "$SUPABASE_DB_URL" -f supabase/rollback/20261101000000_init_schema_down.sql`
(this deletes all TripCut data), then delete version `20261101000000` from `supabase_migrations.schema_migrations`.

## 6. Modal secret
```bash
modal secret create tripcut-api \
  R2_ACCOUNT_ID=... R2_ACCESS_KEY_ID=... R2_SECRET_ACCESS_KEY=... R2_BUCKET=tripcut-media \
  SUPABASE_URL=https://<ref>.supabase.co \
  SUPABASE_DB_URL='postgresql://postgres.<ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres' \
  WEB_ORIGINS='https://<web origin>,http://localhost:5173'
```

## 7. Deploy
```bash
cd tripcut-api
python -m venv .venv && . .venv/bin/activate
pip install -e .
modal deploy infra/modal/serve_api.py
```
Modal prints the URL, e.g. `https://<workspace>--tripcut-api.modal.run`. The API lives under `/v1`.

## 8. Smoke test
Get an access token: sign in on the web app and copy `session.access_token`, or use the Supabase dashboard
(Authentication → Users → the user → "Send magic link", then read the token from the browser session).
```bash
API=https://<workspace>--tripcut-api.modal.run/v1
TOKEN=<access token>
H="Authorization: Bearer $TOKEN"

curl -s -H "$H" $API/me
TRIP=$(curl -s -H "$H" -H 'content-type: application/json' -d '{"title":"smoke"}' $API/trips | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')

# 12 MB test file -> 2 parts (10 MiB + rest)
head -c 12000000 /dev/urandom > /tmp/clip.mp4
CLIP=$(curl -s -H "$H" -H 'content-type: application/json' \
  -d '{"filename":"clip.mp4","content_type":"video/mp4","size_bytes":12000000,"fingerprint":"smoke-1"}' \
  $API/trips/$TRIP/clips | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')
curl -s -H "$H" -H 'content-type: application/json' -d '{"part_numbers":[1,2]}' $API/clips/$CLIP/parts:sign > /tmp/sign.json
URL1=$(python3 -c 'import json;print(json.load(open("/tmp/sign.json"))["parts"][0]["url"])')
URL2=$(python3 -c 'import json;print(json.load(open("/tmp/sign.json"))["parts"][1]["url"])')
head -c 10485760 /tmp/clip.mp4 > /tmp/p1 && tail -c +10485761 /tmp/clip.mp4 > /tmp/p2
curl -s -X PUT --data-binary @/tmp/p1 "$URL1" -o /dev/null -w '%{http_code}\n'   # 200
curl -s -X PUT --data-binary @/tmp/p2 "$URL2" -o /dev/null -w '%{http_code}\n'   # 200
curl -s -H "$H" $API/clips/$CLIP/parts                                         # 2 parts, 12000000 bytes
curl -s -H "$H" -X POST $API/clips/$CLIP/complete                              # status "uploaded"
curl -s -H "$H" -X POST $API/trips/$TRIP/submit                                # 422 too_few_clips (expected)
curl -s -H "$H" -X DELETE $API/trips/$TRIP -o /dev/null -w '%{http_code}\n'    # 204, cleans up
```
Browser CORS check: from the web origin, a presigned `PUT` must succeed and the preflight must list `PUT`.

## 9. Frontend
Set the FE's API base URL to the Modal URL + `/v1` and point it at `docs/api-contract.md`.

## Local run (optional, for developers)
```bash
cp .env.example .env   # fill in values
pip install -e .
uvicorn --factory tripcut_api.app.create_app:create_app --reload --port 8000
```
