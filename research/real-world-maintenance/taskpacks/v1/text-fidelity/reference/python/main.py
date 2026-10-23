"""Native development references and deliberate implementation mutants."""
import json
import sys

MODES = {"baseline": (0, ""), "s1": (1, ""), "s2": (2, ""), "s3": (3, ""),
         "internal_drop": (1, "internal_drop"), "chunk_trim": (2, "chunk_trim"),
         "drop_cdata": (3, "drop_cdata"), "drop_field": (3, "drop_field")}
ASCII_EDGE = " \t\r\n\v\f"


def render(request, stage, mutation):
    if not isinstance(request, dict) or not all(
        name in request and type(request[name]) is kind
        for name, kind in (("cell", str), ("schema", str), ("preserve", bool), ("invalid", bool))
    ):
        raise ValueError("invalid request header")
    schema = "cell.text/1" if stage <= 1 else f"cell.events/{stage}"
    good = not request["invalid"] and request["schema"] == schema
    parts, value = [], ""
    if good and stage <= 1:
        value = request.get("text")
        good = type(value) is str
    elif good:
        events = request.get("events")
        good = type(events) is list
        if good:
            chunks = []
            for event in events:
                if not isinstance(event, dict) or not all(type(event.get(key)) is str for key in ("kind", "value", "style")):
                    good = False
                    break
                kind, text, style = event["kind"], event["value"], event["style"]
                legal = ("text", "reference", "cdata", "run") if stage == 3 else ("text", "reference")
                if kind not in legal:
                    good = False
                    break
                parts.append({"kind": kind, "text": text, "style": style if kind == "run" else ""})
                chunks.append(text.strip(ASCII_EDGE) if mutation == "chunk_trim" else
                              "" if mutation == "drop_cdata" and kind == "cdata" else text)
            value = "".join(chunks)
    if good:
        value = value.replace(" ", "") if mutation == "internal_drop" else value.strip(ASCII_EDGE) if stage > 0 and not request["preserve"] else value
    result = {"cell": request["cell"], "ok": good, "text": value if good else None,
              "error": None if good else "invalid_cell"}
    if stage == 3:
        result.update(characters=len(value) if good else None, parts=parts if good else [])
    if mutation == "drop_field":
        del result["cell"]
    return result


if __name__ == "__main__":
    try:
        if len(sys.argv) != 3 or sys.argv[1] not in MODES:
            raise ValueError("mode and input file required")
        with open(sys.argv[2], encoding="utf-8") as stream:
            requests = json.load(stream)
        if not isinstance(requests, list):
            raise ValueError("expected request array")
        stage, mutation = MODES[sys.argv[1]]
        print(json.dumps([render(item, stage, mutation) for item in requests], ensure_ascii=False))
    except (ValueError, OSError) as error:
        print(error, file=sys.stderr)
        sys.exit(2)
