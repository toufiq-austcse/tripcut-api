# tripcut-api

Python backend for TripCut (SAN-51): FastAPI on Modal, Cloudflare R2 multipart uploads, Supabase Auth + Postgres.

- API contract for the frontend: [`docs/api-contract.md`](docs/api-contract.md) (+ `docs/openapi.json`)
- Rollout steps (run by a person): [`docs/runbooks/rollout.md`](docs/runbooks/rollout.md)
- Schema: [`supabase/migrations/20261101000000_init_schema.sql`](supabase/migrations/20261101000000_init_schema.sql),
  rollback in `supabase/rollback/`
- Week-1 spike CLI `tripcut ./trip --out ./reels` (SAN-48): [`docs/runbooks/tripcut-cli.md`](docs/runbooks/tripcut-cli.md),
  eval set in [`eval/README.md`](eval/README.md)

## Layout

```text
src/tripcut_api/
  app/           create_app, register_routes, app_lifespan
  auth/          Supabase JWT check (JWKS) -> CurrentUser
  config/        Settings + limit/upload/paging constants
  db/            psycopg pool + per-request connection
  dependencies/  service providers for FastAPI Depends
  errors/        ApiError, error codes, exception handlers
  pagination/    keyset cursor encode/decode
  repositories/  SQL per table (one class each)
  routes/        one endpoint per file (me/, trips/, clips/)
  schemas/       one pydantic model per file
  services/      TripService, ClipUploadService
  storage/       R2 client + R2MultipartService (every R2 control call)
src/tripcut_pipeline/   SAN-48 CLI (optional extra `pipeline`; not used by the API image)
  cli.py         `tripcut` entry point -> run_pipeline
  ingest/        ffprobe + one ffmpeg pass -> 360p proxy, 2 fps frames, 16 kHz wav
  score/         PySceneDetect shots, OpenCV blur/exposure/shake, SigLIP, MediaPipe faces + YAMNet
  direct/        Director protocol, ClaudeHaikuDirectorService, FallbackDirectorService
  music/         per-reel track choice (library / user / none) + librosa beat grid (cached)
  render/        beat snap, face-follow 9:16 crop, ffmpeg render + concat, music/clip-sound mix
  metrics/       StageTimerService (wall, core-seconds, peak RSS)
  evaluation/    summary table, trips.csv, blind rating sheet
eval/            run_all.py, make_rating_sheet.py, trips.csv, rating_sheet.csv
assets/music/    3 CC0 tracks (one per reel mood) + LICENSE.md
infra/modal/     Modal app, image and ASGI entry point
infra/r2/        bucket CORS and lifecycle rules
supabase/        CLI config, migration, rollback
```

Code rules: one kind per file (one class, one function, or one set of constants); no `or`/ternary defaults.
