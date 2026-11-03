# sunholo/linkedin — CHANGELOG

## 0.6.2
- Fix: a video over one 4 MB part never uploaded. `std/bytes.slice` takes (offset, length), and the upload
  passed `lastByte + 1` as if it were an end. The first part (offset 0) came out right, but every later part
  asked past the end of the file and the upload stopped with "could not cut bytes …". The cut is now
  `linkedinPartBytes` (exported, tested on a two-part split and past the end). Found on Daneel's first film
  post, a 4,660,380-byte MP4 (3 Nov 2026). 0.6.0 and 0.6.1 should not be used for videos over 4 MB.

## 0.6.1
- Fix: `sunholo/linkedin/videos` imported its sibling as `sunholo/linkedin/posts`, which resolves inside the
  package (its `_smoke.ail` passed) but not from a consumer (`LDR001: module not found`). It now imports
  `pkg/sunholo/linkedin/posts`, as every published package does. Checked from a consumer before publishing.
  0.6.0 should not be used.

## 0.6.0
- New module `sunholo/linkedin/videos`: the Videos API's multipart upload for posts with a video.
  `linkedinInitializeVideoUpload`, `linkedinUploadVideoPart` (returns the part's ETag),
  `linkedinFinalizeVideoUpload`, `linkedinVideoStatus` (poll to `AVAILABLE`), the one-call
  `linkedinUploadVideo`, and `linkedinCreateVideoPost` (`content.media.id` + `title`).
- Proven: `linkedinVideoPartCount` (4 MB parts, enough and not one more) and `linkedinVideoSizeOk`
  (75 KB to 500 MB). Tested: `linkedinPartsCover` refuses instructions with a gap, an overlap, a short
  cover or a part with no URL, before a byte is sent.
- First consumer: Daneel's LinkedIn calendar (sunholo-data/daneel, M-DANEEL-LINKEDIN-MEDIA).
- No existing signature changed.

## 0.5.1
- Fix STRICT_FALLBACK_001 in `comments.ail`: a comments/replies response that
  returns HTTP 200 but is missing the `elements` field is now reported as
  `Err("... missing the 'elements' field ...")` instead of `Ok([])`, so callers'
  `Err` handlers actually fire on malformed responses. A genuine zero-comment
  response (`elements: []`) still returns `Ok([])`.
- No exported signatures changed; `[effects] max` ceiling unchanged.
