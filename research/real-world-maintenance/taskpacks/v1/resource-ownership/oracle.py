"""Independent byte/lifetime oracle. Never imports a submitted implementation."""
import base64
from pathlib import Path


def typed_equal(actual, expected):
    """JSON booleans, numbers, nulls and strings have distinct protocol types."""
    if type(actual) is not type(expected):
        return False
    if isinstance(expected, dict):
        return actual.keys() == expected.keys() and all(typed_equal(actual[k], v) for k, v in expected.items())
    if isinstance(expected, list):
        return len(actual) == len(expected) and all(typed_equal(a, b) for a, b in zip(actual, expected))
    return actual == expected


def validate(request, response, root, stage):
    """Raise AssertionError for a semantic failure; return assertion count."""
    count = 0
    active = {}
    files = {}
    root = Path(root).resolve()

    def check(ok, message):
        nonlocal count
        count += 1
        assert ok, message

    def fail(result, reason):
        check(typed_equal(result, {"ok": False, "error": reason}), f"expected {reason}: {result}")

    def extract(op, result):
        check(type(result) is dict, "extract result must be an object")
        doc = op["doc"]
        if doc in active:
            fail(result, "document_exists")
            return
        values = [base64.b64decode(i["bytes"], validate=True) for i in op["images"]]
        if stage >= 2 and sum(map(len, values)) > op["cap"]:
            fail(result, "byte_cap")
            return
        check(result.get("ok") is True, f"extract failed: {result}")
        refs = result.get("refs")
        check(isinstance(refs, list) and len(refs) == len(values), "wrong ref count")
        paths = []
        for image, payload, ref in zip(op["images"], values, refs):
            check(type(ref) is dict, "reference must be an object")
            check(ref.get("name") == image["name"], "consumer name lost")
            if stage == 0:
                check(ref.get("path") is None, "starter unexpectedly file backed")
                check(ref.get("bytes") == image["bytes"], "inline bytes changed")
            else:
                check(ref.get("bytes") is None, "file migration retained inline bytes")
                check(isinstance(ref.get("path"), str), "file reference missing path")
                path = Path(ref["path"]).resolve()
                check(path.is_relative_to(root) and path != root, "path outside resource directory")
                check(str(path) not in files, "active document/image storage aliases")
                paths.append(str(path))
                files[str(path)] = payload
        active[doc] = {"bytes": [i["bytes"] for i in op["images"]], "paths": paths}

    def step(op, result):
        check(type(result) is dict, "operation result must be an object")
        kind = op["op"]
        if kind == "extract":
            extract(op, result)
        elif kind == "read":
            if op["doc"] not in active:
                fail(result, "document_missing")
            else:
                check(typed_equal(result, {"ok": True, "bytes": active[op["doc"]]["bytes"]}), "read byte ownership changed")
        elif kind == "batch":
            check(stage >= 2, "batch fixture before stage 2")
            check(result.get("ok") is True and isinstance(result.get("results"), list), "batch missing")
            check(len(result["results"]) == len(op["docs"]), "batch result count")
            for doc, member in zip(op["docs"], result["results"]):
                extract({**doc, "cap": op["cap"]}, member)
        elif kind == "release":
            check(stage >= 3, "release fixture before stage 3")
            if op["doc"] not in active:
                fail(result, "document_missing")
            else:
                check(typed_equal(result, {"ok": True}), "release not implemented")
                for path in active[op["doc"]]["paths"]:
                    files.pop(path)
                del active[op["doc"]]
        else:
            raise AssertionError(f"oracle does not know operation {kind}")

    check(type(response) is dict, "response must be an object")
    check(response.get("schema") == request["schema"], "output schema")
    results = response.get("results")
    check(isinstance(results, list) and len(results) == len(request["operations"]), "operation accounting")
    for operation, result in zip(request["operations"], results):
        step(operation, result)
    actual = {str(p.resolve()): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    check(actual == files, "final file bytes/lifetime or atomic rejection changed")
    return count
