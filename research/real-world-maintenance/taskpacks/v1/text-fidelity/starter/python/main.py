"""Native competent baseline. No future stage solution or external delegation."""
import json
import sys


def render(request):
    if not isinstance(request, dict) or not all(
        name in request and type(request[name]) is kind
        for name, kind in (("cell", str), ("schema", str), ("preserve", bool), ("invalid", bool))
    ):
        raise ValueError("invalid request header")
    good = not request["invalid"] and request["schema"] == "cell.text/1" and type(request.get("text")) is str
    return {"cell": request["cell"], "ok": good, "text": request["text"] if good else None,
            "error": None if good else "invalid_cell"}


if __name__ == "__main__":
    try:
        if len(sys.argv) != 3 or sys.argv[1] != "baseline":
            raise ValueError("baseline and input file required")
        with open(sys.argv[2], encoding="utf-8") as stream:
            requests = json.load(stream)
        if not isinstance(requests, list):
            raise ValueError("expected request array")
        print(json.dumps([render(item) for item in requests], ensure_ascii=False))
    except (ValueError, OSError) as error:
        print(error, file=sys.stderr)
        sys.exit(2)
