# Changelog

## 0.2.2

Fix: the GCS backend (Vertex AI) uploads the file's bytes, not its base64 text.

`uploadToGcs` posted the base64 string to GCS's simple upload with
`Content-Transfer-Encoding: base64`. GCS ignores that header on a media upload and stored the
text verbatim, so the object at `uri` was base64 labelled `application/pdf`. Vertex AI refused
every such `gs://` reference with 400 "Request contains an invalid argument". In practice, every
PDF a caller uploaded instead of sending inline failed on Vertex. For example, ailang_parse uploads
PDFs above about 375 KB, so the hosted DocParse `pdfBackend="ai"` failed for every such PDF.

The base64 input is decoded (`std/bytes.fromBase64`) and sent as raw bytes
(`std/net.httpRequestBytes`). Input that is not valid base64 returns `Err` and uploads nothing.
`uploadFile`'s signature and the AI Studio backend are unchanged. Requires ailang >= 0.50.0.

## 0.2.1

Declare the Clock effect `uploadToGcs` uses.
