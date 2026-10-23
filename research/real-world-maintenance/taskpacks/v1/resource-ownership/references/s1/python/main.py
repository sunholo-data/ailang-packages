import base64
import hashlib
import json
from pathlib import Path
import sys


def failure(reason):
    return {"ok": False, "error": reason}


def run(request, root):
    if request["schema"] != "maintenance.resource-ownership/1" or len(request["operations"]) > 64:
        raise ValueError("invalid protocol or operation limit")
    active = {}

    def extract(op):
        doc = op["doc"]
        if doc in active:
            return failure("document_exists")
        images = op["images"]
        if len(images) > 16:
            return failure("image_limit")
        payloads = []
        for image in images:
            payload = base64.b64decode(image["bytes"], validate=True)
            payloads.append(payload)
        if sum(map(len, payloads)) > 16777216:
            return failure("byte_cap")
        refs = []
        for index, (image, payload) in enumerate(zip(images, payloads)):
            path = root / (hashlib.sha256(doc.encode()).hexdigest() + "-" + str(index))
            path.write_bytes(payload)
            ref = {"name": image["name"], "bytes": None, "path": str(path)}
            refs.append(ref)
        active[doc] = refs
        return {"ok": True, "refs": refs}

    def step(op):
        kind = op["op"]
        if kind == "extract":
            return extract(op)
        if kind == "read":
            if op["doc"] not in active:
                return failure("document_missing")
            refs = active[op["doc"]]
            return {"ok": True, "bytes": [base64.b64encode(Path(r["path"]).read_bytes()).decode() for r in refs]}


        return failure("unsupported_operation")

    return {"schema": request["schema"], "results": [step(op) for op in request["operations"]]}


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise ValueError("expected input JSON and resource directory")
    print(json.dumps(run(json.loads(Path(sys.argv[1]).read_text()), Path(sys.argv[2])), sort_keys=True))
