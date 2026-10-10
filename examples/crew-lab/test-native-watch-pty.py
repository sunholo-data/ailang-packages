#!/usr/bin/env python3
"""Hermetic PTY acceptance harness. Product input/rendering is entirely AILANG."""
import fcntl
import glob
import json
import os
import pathlib
import pty
import re
import select
import signal
import struct
import subprocess
import tempfile
import sys
import termios
import time
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parents[2]
AILANG = os.environ.get("AILANG", "ailang")
EVIDENCE = os.environ.get("EVIDENCE_DIR")

# A fixture guardian remains the session leader until attributes are inspected.
# Darwin revokes a controlling PTY when its session leader exits. The AILANG app
# is the only reader of terminal input; the guardian waits on a separate pipe.
GUARDIAN = """import os,subprocess,sys
control=int(sys.argv[1])
p=subprocess.Popen(sys.argv[2:])
print('CREW_FIXTURE_PID='+str(p.pid),flush=True)
rc=p.wait()
print('CREW_FIXTURE_EXIT='+str(rc),flush=True)
os.read(control,1)
sys.exit(rc if rc>=0 else 128-rc)
"""

def visible_cells(frame, columns, rows):
    """Test oracle for this renderer's VT subset, with raw LF retaining column.

    Interpret cursor movement and deferred right-edge wrapping; splitting a byte
    capture into lines cannot establish what a human terminal actually displays.
    Unsupported controls fail instead of silently treating them as printable.
    """
    grid = [[" "] * columns for _ in range(rows)]
    x = y = 0
    pending_wrap = False
    scrolls = 0
    text = frame.decode("utf-8")
    tokens = re.findall(r"\x1b\[[0-9;?]*[A-Za-z]|[^\x1b]", text)
    assert "".join(tokens) == text, "unknown escape in rendered frame"
    for token in tokens:
        if token.startswith("\x1b["):
            if token == "\x1b[2J":
                grid = [[" "] * columns for _ in range(rows)]
            elif token == "\x1b[H":
                x = y = 0
                pending_wrap = False
            else:
                assert token.endswith("m"), f"unsupported renderer control {token!r}"
            continue
        if token == "\r":
            x = 0
            pending_wrap = False
        elif token == "\n":
            y += 1
            pending_wrap = False
        else:
            assert ord(token) >= 32, f"unexpected control {token!r}"
            width = 0 if unicodedata.combining(token) else 2 if unicodedata.east_asian_width(token) in "WF" else 1
            assert width > 0, "fixtures must use standalone display characters"
            if pending_wrap or x + width > columns:
                x = 0
                y += 1
            if y >= rows:
                grid.pop(0)
                grid.append([" "] * columns)
                y = rows - 1
                scrolls += 1
            grid[y][x] = token
            if width == 2:
                grid[y][x + 1] = ""
            x += width
            pending_wrap = x >= columns
            if pending_wrap:
                x = columns - 1
        if y >= rows:
            grid.pop(0)
            grid.append([" "] * columns)
            y = rows - 1
            scrolls += 1
    return ["".join(row) for row in grid], scrolls

# Independent oracle controls: a raw LF really does drift; CRLF and a full-width
# rule followed by CRLF begin the next row at column zero without scrolling.
assert visible_cells(b"ab\ncd", 8, 3)[0][:2] == ["ab      ", "  cd    "]
assert visible_cells(b"ab\r\ncd", 8, 3)[0][:2] == ["ab      ", "cd      "]
assert visible_cells(b"12345678\r\ncd", 8, 3) == (["12345678", "cd      ", "        "], 0)

class Watch:
    def __init__(self, shim, home, columns=80, rows=24):
        self.home = pathlib.Path(home)
        self.master, self.slave = pty.openpty()
        self.original = termios.tcgetattr(self.slave)
        self.resize(columns, rows, notify=False)
        control,self.control= os.pipe()
        self.proc = subprocess.Popen([sys.executable,"-u","-c",GUARDIAN,str(control),str(shim), "--mode", "native", "--home", str(home), "--seed", "42"], pass_fds=(control,), stdin=self.slave, stdout=self.slave, stderr=self.slave, start_new_session=True, env={**os.environ, "TERM": "xterm-256color"})
        os.close(control)
        print(f"fixture pid={self.proc.pid} home={self.home.name}", flush=True)
        self.output = b""
        self.mark = 0

    def resize(self, columns, rows, notify=True):
        fcntl.ioctl(self.slave, termios.TIOCSWINSZ, struct.pack("HHHH", rows, columns, 0, 0))
        if notify:
            os.kill(self.worker_pid(), signal.SIGWINCH)

    def drain(self, duration=.15):
        deadline = time.monotonic() + duration
        while time.monotonic() < deadline:
            ready, _, _ = select.select([self.master], [], [], max(0, deadline-time.monotonic()))
            if ready:
                try:
                    chunk = os.read(self.master, 65536)
                except OSError:
                    break
                if not chunk:
                    break
                self.output += chunk

    def expect(self, text, timeout=45):
        needle = text.encode()
        deadline = time.monotonic()+timeout
        while needle not in self.output[self.mark:]:
            if time.monotonic() >= deadline:
                raise AssertionError(f"Timeout waiting for {text!r}; tail={self.output[-1600:]!r}")
            self.drain(.1)
        self.mark = self.output.find(needle,self.mark)+len(needle)

    def send(self, keys):
        os.write(self.master, keys)

    def journal(self):
        files = list(self.home.glob("runs/*/journal.jsonl"))
        assert len(files)==1, files
        return files[0]

    def worker_pid(self):
        match=re.search(rb"CREW_FIXTURE_PID=(\d+)",self.output)
        assert match, "missing fixture worker PID"
        return int(match.group(1))

    def wait_exit(self, timeout=30):
        deadline=time.monotonic()+timeout
        while True:
            match=re.search(rb"CREW_FIXTURE_EXIT=(-?\d+)",self.output)
            if match:
                self.drain(.1)
                return int(match.group(1))
            if time.monotonic()>deadline:
                raise AssertionError("Timed out waiting for native host exit")
            self.drain(.1)

    def restored(self):
        self.drain(.1)
        if EVIDENCE:
            pathlib.Path(EVIDENCE).mkdir(parents=True,exist_ok=True)
            (pathlib.Path(EVIDENCE)/f"{self.home.name}-raw.ansi").write_bytes(self.output)
        restored=termios.tcgetattr(self.slave)
        original=list(self.original)
        original[3] &= ~getattr(termios,"PENDIN",0)
        restored[3] &= ~getattr(termios,"PENDIN",0)
        assert restored==original, f"termios not restored: {original!r} != {restored!r}"
        assert b"\x1b[?1049l" in self.output, "alternate screen not restored"
        assert b"\x1b[?25h" in self.output, "cursor not restored"

    def close(self):
        try:
            os.write(self.control,b"x")
            deadline=time.monotonic()+10
            while self.proc.poll() is None and time.monotonic()<deadline:
                self.drain(.1)
            if self.proc.poll() is None:
                os.killpg(self.proc.pid,signal.SIGKILL)
                self.proc.wait(timeout=10)
        finally:
            os.close(self.control)
            os.close(self.master)
            os.close(self.slave)

def completed_payload(w):
    return [json.loads(line)["payload"] for line in w.journal().read_text().splitlines()]

with tempfile.TemporaryDirectory(prefix="crew-native-pty-") as temporary:
    base = pathlib.Path(temporary)
    subprocess.run([AILANG,"install","--path",str(ROOT/"examples/crew-lab"),"--bin-dir",str(base/"bin")],check=True,stdout=subprocess.DEVNULL)
    shim = base/"bin/crew-watch-offline"
    w = Watch(shim,base/"journey")
    try:
        w.expect("Start despite refusal; trust can fall.")
        attrs=termios.tcgetattr(w.slave)
        assert not attrs[3]&termios.ICANON and not attrs[3]&termios.ECHO
        w.send(b"1")
        w.expect("Choice 1/6")
        w.send(b"1")
        w.expect("1 scientist:")
        w.send(b"1")
        w.expect("scientist agreed. Work has not started.")
        before=w.journal().read_bytes()
        w.resize(20,8)
        w.expect("Need 40 x 16")
        w.send(b"1\r")
        w.drain(.3)
        assert w.journal().read_bytes()==before, "tiny view dispatched hidden action"
        w.resize(40,16)
        w.expect("Decide later")
        w.send(b"h")
        w.expect("READING / no time or resources used")
        w.send(b"b")
        w.expect("> 2 Decide later")
        w.send(b"q")
        w.expect("END WATCH?")
        w.send(b"\r")
        w.expect("> 2 Decide later")
        w.resize(100,30)
        w.expect("Decide later")
        w.resize(220,70)
        w.expect("Decide later")
        assert w.journal().read_bytes()==before, "navigation/resize/quit-cancel changed journal"
        w.send(b"\x1b[A\r")
        w.expect("VOYAGE / BRIDGE / turn 0")
        for tick in range(1,5):
            w.send(b"5")
            w.expect(f"VOYAGE / BRIDGE / turn {tick}")
            if tick==3:
                w.expect("3/4 turns")
        payloads=completed_payload(w)
        states=[json.loads(p["host_output"])["state"] for p in payloads if "host_output" in p and "state" in json.loads(p["host_output"])]
        assert states[-1]["tick"]==4
        assert any(t["status"]=="completed" for t in states[-1]["tasks"])
        assert all(p.get("metadata",{}).get("usage",{}).get("calls",0)==0 for p in payloads)
        w.send(b"q")
        w.expect("END WATCH?")
        w.send(b"\x1b[B\r")
        assert w.wait_exit(30)==0
        w.restored()
        # Inspect actual completed native frames, preserving fixed spaces.
        frames=w.output.split(b"\x1b[2J\x1b[H")[1:-1]
        inspected=[]
        for chunk in frames:
            text=re.sub(rb"\x1b\[[0-9;?]*[A-Za-z]",b"",chunk).decode("utf-8").replace("\r","")
            lines=text.split("\n")
            if "Terminal too small" in text:
                assert len(lines)<=8 and all(len(line)<=20 for line in lines)
                visible, scrolls = visible_cells(b"\x1b[2J\x1b[H" + chunk, 20, 8)
                assert scrolls == 0 and visible == [line.ljust(20) for line in lines] + [" " * 20] * (8 - len(lines))
                inspected.append((20,8))
                continue
            rule=next(line for line in lines if line and set(line)<=set("─-"))
            columns=len(rule)
            rows={80:24,40:16,100:30,160:60}[columns]
            assert len(lines)==rows, (columns,len(lines),lines)
            assert all(len(line)<=columns for line in lines), (columns,lines)
            physical_columns, physical_rows = (220, 70) if columns == 160 else (columns, rows)
            visible, scrolls = visible_cells(b"\x1b[2J\x1b[H" + chunk, physical_columns, physical_rows)
            assert scrolls == 0, f"frame scrolled {scrolls} rows at {columns}x{rows}"
            assert visible == [line.ljust(physical_columns) for line in lines] + [" " * physical_columns] * (physical_rows - rows), f"native cursor drift at {physical_columns}x{physical_rows}: {visible!r}"
            if EVIDENCE:
                (pathlib.Path(EVIDENCE)/f"visible-{physical_columns}x{physical_rows}.txt").write_text("\n".join(visible) + "\n")
            inspected.append((columns,rows))
        assert {(80,24),(20,8),(40,16),(100,30),(160,60)}<=set(inspected)
        if EVIDENCE:
            pathlib.Path(EVIDENCE).mkdir(parents=True,exist_ok=True)
            (pathlib.Path(EVIDENCE)/"native-journey.ansi").write_bytes(w.output.replace(str(base).encode(),b"<temporary-home>"))
        print("PASS native visible cursor cells/no scrolling, arrows/Enter, proposal-safe quit, resize80/20/40/100/220, real four-turn completion and restoration")
    finally:
        w.close()

    w=Watch(shim,base/"interrupt")
    try:
        w.expect("Start despite refusal; trust can fall.")
        os.kill(w.worker_pid(),signal.SIGINT)
        w.wait_exit(20)
        w.restored()
        assert not (base/"interrupt/runs").exists()
        print("PASS actual interruption restores raw/cursor/alternate screen without a confirmation")
    finally:
        w.close()

    w=Watch(shim,base/"failure")
    try:
        w.expect("Start despite refusal; trust can fall.")
        w.send(b"1")
        w.expect("Choice 1/6")
        journal=w.journal()
        before=journal.read_bytes()
        pathlib.Path(str(journal)+".tmp").mkdir()
        w.send(b"1")
        w.expect("1 scientist:")
        w.send(b"1")
        assert w.wait_exit(30)==1
        w.restored()
        assert journal.read_bytes()==before
        assert b"Journal failed" in w.output
        print("PASS injected host-publication failure restores terminal and preserves journal prefix")
    finally:
        w.close()
