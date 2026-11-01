# TripCut API contract (v1)

Owner: backend (SAN-51). The frontend (SAN-54/55) builds against this document.
Machine-readable: `docs/openapi.json` (snapshot) and the live `GET /v1/openapi.json` (docs UI at `/v1/docs`).

- **Base URL:** `https://<workspace>--tripcut-api.modal.run/v1` (local: `http://localhost:8000/v1`)
- **Auth:** every endpoint needs `Authorization: Bearer <Supabase access token>` (from Supabase JS `session.access_token`).
- **JSON:** snake_case. Times are ISO 8601 UTC. Ids are UUIDs.
- **Errors:** `{"error": {"code": "clip_limit", "message": "A trip holds at most 100 clips"}}`. Switch on `code`, show `message` only for debugging.

## Upload flow

```text
 client
   |1 GET  /me                                 -> limits (part size, clip and byte limits)
   |2 POST /trips {title}                      -> Trip (status "open")
   |3 for each file:
   |    POST /trips/{trip_id}/clips {filename, content_type, size_bytes, fingerprint}
   |       201 new Clip, or 200 the same Clip again (same fingerprint = resume)
   |       if clip.status == "uploaded": skip this file
   |    GET  /clips/{clip_id}/parts            -> parts already in R2 (resume after reload)
   |    POST /clips/{clip_id}/parts:sign {part_numbers:[..]}  -> presigned URLs (1 h)
   |    PUT  <url> with bytes [ (n-1)*part_size_bytes, n*part_size_bytes )   -> straight to R2
   |    POST /clips/{clip_id}/complete         (empty body) -> Clip status "uploaded"
   |4 POST /trips/{trip_id}/submit             -> 202, trip "processing", latest_job "queued"
   |5 GET  /trips/{trip_id}                    -> poll trip.status and latest_job.step
   v
```

Part rules: part `n` is the byte range `[(n-1) * part_size_bytes, min(n * part_size_bytes, size_bytes))`.
`part_count = ceil(size_bytes / part_size_bytes)`. Every part except the last must be exactly `part_size_bytes`
(10 MiB). The PUT needs no headers except an optional `Content-Type`; the client does **not** need to read ETags.
Sign at most 100 part numbers per call; re-sign when a URL expires (403 from R2).

Fingerprint: any string that is stable for the same file on the same device, for example
`` `${file.name}:${file.size}:${file.lastModified}` ``. Same fingerprint with a different `size_bytes` is a 422.

## Objects

```text
<Trip> = {
  "id": "7c1d...", "title": "Lisbon, 3 days",
  "status": "open" | "processing" | "ready" | "failed",
  "notify_email": true,
  "clip_count": 42, "total_bytes": 1932735283, "uploaded_clip_count": 40,
  "submitted_at": null, "created_at": "2026-11-01T10:00:00Z", "updated_at": "2026-11-01T10:05:00Z"
}
<Clip> = {
  "id": "c9a2...", "trip_id": "7c1d...", "filename": "IMG_0412.MOV", "content_type": "video/quicktime",
  "size_bytes": 734003200, "fingerprint": "IMG_0412.MOV:734003200:1761990000000",
  "status": "uploading" | "uploaded",
  "part_size_bytes": 10485760, "part_count": 70,
  "uploaded_at": null, "created_at": "2026-11-01T10:01:00Z"
}
<Job> = {
  "id": "j5e0...", "kind": "analyze" | "rerender",
  "status": "queued" | "running" | "succeeded" | "failed",
  "step": null | "ingest" | "score" | "direct" | "music" | "render" | "notify",
  "attempt": 0, "error": null, "started_at": null, "finished_at": null, "created_at": "2026-11-01T10:30:00Z"
}
<TripDetail> = <Trip> + { "clips": [<Clip>], "latest_job": <Job> | null }
```

## Endpoints

| # | Method + path | Request body | Success |
|---|---|---|---|
| 1 | `GET /me` | – | `200 {"id","email","limits":{"max_open_trips":3,"min_clips":10,"max_clips":100,"max_trip_bytes":3221225472,"part_size_bytes":10485760,"max_parts_per_sign":100,"allowed_content_type_prefix":"video/"}}` |
| 2 | `POST /trips` | `{"title":"Lisbon, 3 days"}` (1–200 chars) | `201 <Trip>` |
| 3 | `GET /trips?limit=20&cursor=<c>` | – | `200 {"items":[<Trip>],"next_cursor":"<c>" \| null}` newest first; `limit` 1–100 |
| 4 | `GET /trips/{trip_id}` | – | `200 <TripDetail>` (clips oldest first) |
| 5 | `PATCH /trips/{trip_id}` | `{"title":"Lisbon 2026","notify_email":false}` (both optional) | `200 <Trip>` |
| 6 | `DELETE /trips/{trip_id}` | – | `204`. Not while `processing`. Aborts open uploads, deletes stored objects and all rows. |
| 7 | `POST /trips/{trip_id}/clips` | `{"filename":"IMG_0412.MOV","content_type":"video/quicktime","size_bytes":734003200,"fingerprint":"IMG_0412.MOV:734003200:1761990000000"}` | `201 <Clip>` new; `200 <Clip>` same fingerprint (resume) |
| 8 | `POST /clips/{clip_id}/parts:sign` | `{"part_numbers":[1,2,3,4]}` | `200 {"parts":[{"part_number":1,"url":"https://<acct>.r2.cloudflarestorage.com/tripcut-media/originals/...","expires_at":"2026-11-01T11:00:00Z"}]}` |
| 9 | `GET /clips/{clip_id}/parts` | – | `200 {"parts":[{"part_number":1,"size_bytes":10485760}],"uploaded_bytes":10485760}` |
| 10 | `POST /clips/{clip_id}/complete` | none | `200 <Clip>` with `status:"uploaded"`. Safe to retry. |
| 11 | `DELETE /clips/{clip_id}` | – | `204`. Trip must be `open`. A second call returns `404`. |
| 12 | `POST /trips/{trip_id}/submit` | none | `202 <TripDetail>` with `status:"processing"` and `latest_job.status:"queued"` |

## Error codes

| Status | Code | When |
|---|---|---|
| 401 | `unauthorized` | missing, expired or invalid token |
| 404 | `not_found` | id does not exist **or** belongs to another user (never 403) |
| 405 | `method_not_allowed` | wrong HTTP method |
| 409 | `open_trip_limit` | already 3 trips in `open` or `processing` |
| 409 | `trip_not_open` | clip write or submit on a trip that is not `open`; delete while `processing` |
| 409 | `clip_not_uploading` | sign or complete on an `uploaded` clip |
| 409 | `clips_incomplete` | submit while a clip is still `uploading` |
| 409 | `parts_incomplete` | complete while R2 is missing parts or bytes (message says how many) |
| 413 | `trip_size_limit` | the clip would push the trip over 3 GB |
| 413 | `clip_limit` | the trip already has 100 clips |
| 415 | `unsupported_media_type` | `content_type` is not `video/*` |
| 422 | `too_few_clips` | submit with fewer than 10 clips |
| 422 | `validation_error` | bad body, bad id, bad cursor, part number outside `1..part_count`, fingerprint reused with another size |
| 500 | `internal_error` | bug; check logs |
| 502 | `storage_error` | an R2 call failed; safe to retry |

## Notes for the frontend

- The browser talks to R2 only with presigned `PUT`s. R2 CORS allows `PUT` with `content-type` from the web origin.
- On reload: `GET /trips/{id}` → for each `uploading` clip, `GET /clips/{id}/parts` → sign and PUT only the missing parts → `complete`.
- To drop a file before submit: `DELETE /clips/{id}`.
- Unfinished uploads are removed by R2 after 1 day; the clip row then fails `complete` with `storage_error`.
  Delete the clip and add it again.
- Browsers can also read their own rows straight from Supabase (RLS select-only), but the API is the supported path.
