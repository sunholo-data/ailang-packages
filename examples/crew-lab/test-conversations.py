#!/usr/bin/env python3
"""Hermetic installed conversation acceptance; Python is only a PTY/journal oracle.

Product editor, policy, dialogue and simulation remain pure AILANG. This harness
never opens user homes or calls a provider. Run after M1/M3 are integrated.
"""
import pathlib
import os
import sys

# Reuse the established fixture guardian, terminal-restoration checks and VT cell
# oracle without running the earlier journey suite. Its top-level suite begins at
# this exact marker; fail loudly if that helper layout changes.
HELPER = pathlib.Path(__file__).with_name("test-native-watch-pty.py")
helper_source = HELPER.read_text()
helper_prefix, separator, _ = helper_source.partition("with tempfile.TemporaryDirectory")
assert separator, "native PTY helper entry marker changed"
exec(compile(helper_prefix, str(HELPER), "exec"), globals())

SEED = 34500  # Authored policy naturally selects a concern for the first medic offer.
QUOTE = "qbh0 café"

class ConversationWatch(Watch):
    def __init__(self, shim, home, columns=80, rows=30):
        self.home = pathlib.Path(home)
        self.master, self.slave = pty.openpty()
        self.original = termios.tcgetattr(self.slave)
        self.resize(columns, rows, notify=False)
        control, self.control = os.pipe()
        self.proc = subprocess.Popen(
            [sys.executable, "-u", "-c", GUARDIAN, str(control), str(shim),
             "--mode", "native", "--home", str(home), "--seed", str(SEED)],
            pass_fds=(control,), stdin=self.slave, stdout=self.slave,
            stderr=self.slave, start_new_session=True,
            env={**os.environ, "TERM": "xterm-256color"})
        os.close(control)
        self.output = b""
        self.mark = 0


def payloads(home):
    files = list(pathlib.Path(home).glob("runs/*/journal.jsonl"))
    assert len(files) == 1, files
    return [json.loads(line)["payload"] for line in files[0].read_text().splitlines()]


def inputs(home):
    return [json.loads(p["host_input"]) for p in payloads(home) if "host_input" in p]


def states(home):
    result = []
    for p in payloads(home):
        if "host_output" in p:
            output = json.loads(p["host_output"])
            if "state" in output:
                result.append(output["state"])
    return result


def economic(state):
    return {"tick": state["tick"], "resources": state["resources"], "tasks": state["tasks"]}


def captain_inputs(home):
    return [c for c in inputs(home) if c.get("command") == "captain_reply"]


def await_reconsideration(w, output_start, timeout=45):
    """Wait for a committed response, allowing disagreement to remain open."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        w.drain(.1)
        spoken = captain_inputs(w.home)
        if len(spoken) != 1:
            continue
        responses = [c for c in inputs(w.home)
                     if c.get("command") == "answer"
                     and c.get("request") == "reconsider-" + spoken[0]["id"]]
        fresh = w.output[output_start:]
        decision_rendered = any(header in fresh for header in
                                (b"VOYAGE / PROPOSAL / turn 0",
                                 b"VOYAGE / TALK THROUGH THE CONCERN / turn 0"))
        if len(responses) == 1 and decision_rendered:
            return
    raise AssertionError("Captain speech did not receive a new same-proposal response")


def replay_boundaries(home, base, stale=False):
    """AILANG replays every recorded boundary; Python compares exact output."""
    recorded = [p for p in payloads(home)
                if "host_input" in p and "host_output" in p]
    commands = [p["host_input"] for p in recorded]
    expected = [p["host_output"] for p in recorded]
    inserted = None
    if stale:
        inserted = next(i for i, command in enumerate(commands)
                        if json.loads(command).get("command") == "captain_reply")
        invalid = json.loads(commands[inserted])
        invalid.update(id="stale-captain", tick=invalid["tick"] + 1)
        commands.insert(inserted, json.dumps(invalid, ensure_ascii=False))
    args = base / (home.name + ("-stale" if stale else "") + "-inputs.json")
    args.write_text(json.dumps(commands, ensure_ascii=False))
    for engine in ("evaluator", "strict-vm"):
        flags = [] if engine == "evaluator" else ["--bytecode", "--strict-bytecode"]
        result = subprocess.run([AILANG, "run", *flags, "--package-dir",
                                 str(ROOT / "examples/crew-lab"), "--entry",
                                 "recoveryRecording", "--args-file", str(args),
                                 str(ROOT / "examples/crew-lab/play_flow.ail")],
                                capture_output=True, text=True, timeout=60)
        assert result.returncode == 0, result.stderr
        actual = result.stdout.splitlines()
        if inserted is not None:
            rejected = json.loads(actual.pop(inserted))
            assert "stale" in rejected.get("error", {}).get("host", ""), rejected
        assert actual == expected, f"{home.name} {engine} changed recorded boundaries"
        if EVIDENCE:
            directory = pathlib.Path(EVIDENCE)
            directory.mkdir(parents=True, exist_ok=True)
            label = home.name + ("-stale" if stale else "")
            (directory / f"{label}-{engine}.ndjson").write_text(result.stdout)
            (directory / f"{label}-inputs.json").write_text(args.read_text())


def zero_provider(home):
    for p in payloads(home):
        assert p.get("metadata", {}).get("usage", {}).get("calls", 0) == 0, p
    assert all(p.get("mode", "offline") == "offline" for p in payloads(home))


def initial_concern(w):
    w.expect("Start despite refusal; trust can fall.")
    w.send(b"1")
    w.expect("VOYAGE / BRIDGE / turn 0")
    w.send(b"1")
    w.expect("VOYAGE / CHOOSE WORK / turn 0")
    w.send(b"3")
    w.expect("VOYAGE / TALK THROUGH THE CONCERN / turn 0")
    records = payloads(w.home)
    selected = [p.get("metadata", {}).get("selection", {}).get("selected_label") for p in records]
    assert "concern" in selected, "seed fixture did not select medic concern"
    state = states(w.home)[-1]
    assert state["tick"] == 0 and len(state["tasks"]) == 1
    task = state["tasks"][0]
    assert task["recipe"] == "work_medic" and task["status"] == "offered"
    assert all(r["reserved"] == 0 and r["consumed"] == 0 for r in state["resources"])
    return state


def frame_fit(w, columns, rows, label):
    w.drain(.2)
    chunk = w.output.rsplit(b"\x1b[2J\x1b[H", 1)[-1]
    frame = b"\x1b[2J\x1b[H" + chunk
    visible, scrolls = visible_cells(frame, columns, rows)
    assert scrolls == 0, (label, columns, rows, scrolls)
    text = re.sub(rb"\x1b\[[0-9;?]*[A-Za-z]", b"", chunk).decode().replace("\r", "")
    lines = text.split("\n")
    assert len(lines) == rows and all(len(line) <= columns for line in lines), (label, lines)
    assert visible == [line.ljust(columns) for line in lines], f"cursor drift in {label}"
    if EVIDENCE:
        directory = pathlib.Path(EVIDENCE)
        directory.mkdir(parents=True, exist_ok=True)
        (directory / f"conversation-{label}-{columns}x{rows}.txt").write_text("\n".join(visible) + "\n")


def quit_watch(w):
    w.send(b"q")
    w.expect("END WATCH?")
    w.send(b"\x1b[B\r")
    assert w.wait_exit() == 0
    w.restored()
    zero_provider(w.home)


def plain(shim, home, commands, columns=100, rows=40):
    run = subprocess.run([str(shim), "--mode", "plain", "--home", str(home),
                          "--seed", str(SEED), "--columns", str(columns), "--rows", str(rows)],
                         input=commands, text=True, capture_output=True, timeout=60)
    assert run.returncode == 0, run.stdout[-2000:] + run.stderr[-2000:]
    assert "TALK THROUGH THE CONCERN" in run.stdout
    zero_provider(home)
    if EVIDENCE:
        directory = pathlib.Path(EVIDENCE)
        directory.mkdir(parents=True, exist_ok=True)
        (directory / f"conversation-{home.name}.txt").write_text(run.stdout.replace(str(home), "<temporary-home>"))
    return run.stdout


with tempfile.TemporaryDirectory(prefix="crew-conversation-acceptance-") as temporary:
    base = pathlib.Path(temporary)
    subprocess.run([AILANG, "install", "--path", str(ROOT / "examples/crew-lab"),
                    "--bin-dir", str(base / "bin")], check=True, stdout=subprocess.DEVNULL)
    shim = base / "bin/crew-watch-offline"

    # Actual native input: menu letters remain text; Unicode, erase, left/right,
    # help, resizing and review cannot accidentally send speech or start work.
    w = ConversationWatch(shim, base / "native-speech")
    try:
        prior_state = initial_concern(w)
        before = w.journal().read_bytes()
        w.send(b"4")
        w.expect("WRITE A REPLY")
        w.send("qbh0 cafè".encode())
        w.send(b"\x7f")
        w.send("é".encode())
        w.expect(QUOTE)
        w.send(b"\x1b[D\x1b[C")
        w.send(b"\t")
        w.expect("VOYAGE / HELP")
        w.send(b"b")
        w.expect("WRITE A REPLY")
        for columns, rows in ((40, 16), (100, 40), (80, 30)):
            w.resize(columns, rows)
            w.expect("WRITE A REPLY")
            frame_fit(w, columns, rows, "editor")
        assert w.journal().read_bytes() == before, "typing/help/resize sent speech"
        w.send(b"\r")
        w.expect("REVIEW YOUR REPLY")
        w.send(b"3")  # Explicit interpretation changes, exact prose does not.
        w.expect("Discuss a staged approach")
        w.send(b"2")
        w.expect("WRITE A REPLY")
        assert w.journal().read_bytes() == before, "review/edit changed journal"
        w.send(b"\r")
        w.expect("REVIEW YOUR REPLY")
        output_start = len(w.output)
        w.send(b"1")
        await_reconsideration(w, output_start)
        spoken = captain_inputs(w.home)
        assert len(spoken) == 1 and spoken[0]["text"] == QUOTE, spoken
        assert spoken[0]["approach"] == "stage_plan", spoken
        assert economic(states(w.home)[-1]) == economic(prior_state), "speech changed work/resources/time"
        assert len(states(w.home)[-1]["tasks"]) == 1, "reply reoffered a new project"
        quit_watch(w)
        replay_boundaries(w.home, base)
        replay_boundaries(w.home, base, stale=True)
        print("PASS native literal menu letters/Unicode/editor/help/resize/review, exact speech and same offered project")
    finally:
        w.close()

    # Editing an authored suggestion and then cancelling sends nothing. Quit
    # appends its own lifecycle record, so compare before opening confirmation.
    w = ConversationWatch(shim, base / "native-cancel", 100, 40)
    try:
        initial_concern(w)
        before = w.journal().read_bytes()
        w.send(b"1")
        w.expect("WRITE A REPLY")
        w.send(" café".encode())
        w.expect("café")
        w.send(b"\r")
        w.expect("REVIEW YOUR REPLY")
        w.send(b"0")
        w.expect("TALK THROUGH THE CONCERN")
        assert w.journal().read_bytes() == before and captain_inputs(w.home) == []
        w.send(b"4")
        w.expect("WRITE A REPLY")
        w.send(b"\x1b")
        w.expect("TALK THROUGH THE CONCERN")
        assert w.journal().read_bytes() == before and captain_inputs(w.home) == []
        quit_watch(w)
        replay_boundaries(w.home, base)
        print("PASS editable suggestion, review cancellation and native Escape preserve pending concern")
    finally:
        w.close()

    prefix = "1\n1\n3\n"
    plain(shim, base / "plain-speech", prefix + "4\n" + QUOTE + "\n\n3\n2\n\n1\n")
    spoken = captain_inputs(base / "plain-speech")
    assert len(spoken) == 1 and spoken[0]["text"] == QUOTE and spoken[0]["approach"] == "stage_plan"
    ps = states(base / "plain-speech")
    assert economic(ps[-1]) == economic(ps[3]), "plain speech changed offered work/time/resources"
    replay_boundaries(base / "plain-speech", base)
    for name, suffix in (("plain-eof", "4\n" + QUOTE + "\n"),
                         ("plain-cancel", "4\n" + QUOTE + "\n/cancel\n"),
                         ("plain-review-eof", "4\n" + QUOTE + "\n\n")):
        home = base / name
        plain(shim, home, prefix + suffix, 40, 16)
        assert captain_inputs(home) == [], "EOF/cancel implicitly sent draft"
        assert len(states(home)[-1]["tasks"]) == 1 and states(home)[-1]["tick"] == 0
        replay_boundaries(home, base)
    print("PASS installed plain exact Unicode speech, explicit approach, draft/review EOF and cancel send nothing")

    # A major fixture is an explicit received report; inspecting it is free,
    # while only Advance projects gradual personality into the live actors.
    major_home = base / "plain-major"
    major = subprocess.run([str(shim), "--mode", "plain", "--debug", "--home", str(major_home),
                            "--seed", str(SEED), "--columns", "100", "--rows", "40"],
                           input="1\n4\n1\nc\nb\n5\nc\n", text=True,
                           capture_output=True, timeout=60)
    assert major.returncode == 0, major.stdout[-2000:] + major.stderr[-2000:]
    major_states = states(major_home)
    assert len(major_states) == 3 and major_states[-1]["tick"] == 1, major_states
    assert economic(major_states[0]) == economic(major_states[1]), "report changed work, resources or clock"
    assert [a["attributes"] for a in major_states[0]["actors"]] == [a["attributes"] for a in major_states[1]["actors"]], "instant trait jump"
    assert [a["attributes"] for a in major_states[1]["actors"]] != [a["attributes"] for a in major_states[2]["actors"]], "Advance did not apply drift"
    assert "PERSONALITY RESPONSE / DEVELOPMENT" in major.stdout and "lab report" in major.stdout
    zero_provider(major_home)
    replay_boundaries(major_home, base)
    print("PASS installed lab major report, free inspection, no instant jump, gradual Advance and exact replay")
