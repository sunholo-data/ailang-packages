#!/usr/bin/env python3
"""Acceptance harness only: the installed live watch in native mode on a real PTY.
Words prepared by a slow fixture worker must appear while no key is pressed, and
quitting must leave no worker. Product input/rendering is entirely AILANG.
Usage: test-async-pty.py BIN_DIR WORKER_DIR HOME"""
import fcntl, os, pty, re, select, signal, struct, subprocess, sys, termios, time

signal.alarm(90)  # a hung watch fails the check instead of hanging it

bin_dir, worker_dir, home = sys.argv[1:4]
env = dict(os.environ, PATH=f"{worker_dir}:/usr/bin:/bin", CREW_FIXTURE_DELAY_MS="1500", TERM="xterm-256color")
args = [f"{bin_dir}/crew-watch", "--mode", "native", "--legacy", "--prefetch", "0", "--home", home, "--seed", "42"]
pid, fd = pty.fork()
if pid == 0:
    os.execve(args[0], args, env)
fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", 30, 100, 0, 0))
seen = b""

def read_until(pattern, seconds):
    global seen
    deadline = time.time() + seconds
    while time.time() < deadline:
        r, _, _ = select.select([fd], [], [], 0.1)
        if r:
            try:
                chunk = os.read(fd, 65536)
            except OSError:
                break
            seen += chunk
            if re.search(pattern, seen):
                return
    os.kill(pid, signal.SIGKILL)
    sys.exit(f"timed out waiting for {pattern!r}; tail: {seen[-600:]!r}")

def key(k):
    os.write(fd, k)
    time.sleep(0.25)

read_until(rb"Ask for agreement", 20)
for k in (b"1", b"1", b"1"):
    key(k)
read_until(rb"Replies: 1 preparing, 0 new", 20)
mark = len(seen)
# No keys from here: only the watch's own polling can show the arrival.
read_until(rb"Replies: 0 preparing, 1 new", 20)
assert b"Replies: 0 preparing, 1 new" in seen[mark:], "arrival not drawn while idle"
key(b"r")
read_until(rb"\(fixture words, accept\)", 10)
key(b"q")
key(b"\x1b[B")
key(b"\r")
read_until(rb"END OF YOUR PREPARATION WATCH", 20)
# Drain the rest of the recap until the watch closes the terminal, then reap it.
while True:
    r, _, _ = select.select([fd], [], [], 5)
    if not r:
        break
    try:
        if not os.read(fd, 65536):
            break
    except OSError:
        break
_, status = os.waitpid(pid, 0)
if status != 0:
    sys.exit(f"watch exited with status {status}")
time.sleep(0.3)
left = subprocess.run(["pgrep", "-f", f"{os.path.basename(os.path.dirname(home))}/.*/replies/job-"], capture_output=True, text=True).stdout.split()
if left:
    sys.exit(f"workers left after quit: {left}")
print("native PTY: background words drawn while idle, read with r, no worker left")
