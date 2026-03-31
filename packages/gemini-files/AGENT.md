# sunholo/gemini_files

Upload large files for Gemini AI multimodal calls. Eliminates redundant base64 re-transmission by uploading once and referencing by URI.

## Quick Start

```ailang
import pkg/sunholo/gemini_files/upload (uploadFile, deleteFile, UploadedFile)

-- Upload a PDF for use in AI calls
match uploadFile(base64Data, "application/pdf", "contract.pdf") {
  Ok(uploaded) => {
    -- Use uploaded.uri in AI calls:
    -- For GCS backend: "gs://bucket/docparse-temp/123-contract.pdf"
    -- For AI Studio:   "https://generativelanguage.googleapis.com/v1beta/files/abc123"
    println("Uploaded: " ++ uploaded.uri);

    -- ... make AI calls with fileUri instead of inline data ...

    -- Cleanup
    deleteFile(uploaded)
  },
  Err(e) => println("Upload unavailable, using inline: " ++ e)
}
```

## Backend Auto-Detection

| Priority | Condition | Backend | URI Format |
|----------|-----------|---------|------------|
| 1 | `GOOGLE_API_KEY=""` + `GCS_TEMP_BUCKET` set | GCS (Vertex AI) | `gs://bucket/path` |
| 2 | `GOOGLE_API_KEY` set | AI Studio Files API | Gemini file URI |
| 3 | Neither | Returns `Err` | Caller falls back to inline |

## Functions

| Function | Signature | Effect |
|----------|-----------|--------|
| `uploadFile` | `(base64Data, mimeType, displayName) -> Result[UploadedFile, string]` | `{Net, FS, Env}` |
| `deleteFile` | `(uploaded: UploadedFile) -> Result[(), string]` | `{Net, FS, Env}` |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GCS_TEMP_BUCKET` | For Vertex AI | GCS bucket name (e.g. `docparse-temp-files`) |
| `GOOGLE_API_KEY` | For AI Studio | Google AI Studio API key |

## UploadedFile Type

```ailang
type UploadedFile = {
  uri: string,       -- File URI for AI calls (gs:// or https://)
  mimeType: string,  -- MIME type of uploaded file
  backend: string,   -- "gcs" or "ai_studio"
  ref: string        -- Backend reference for deletion
}
```

## Dependencies

- `sunholo/gcp_auth` — OAuth2 tokens for GCS uploads (ADC)
- `sunholo/http_helpers` — HTTP request builders
