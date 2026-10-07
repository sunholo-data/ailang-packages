"""Widget HTML sanity: well-formed (every non-void element closed, in order),
exactly one file picker, exactly two inline module scripts and no external
resource (src/href/@import/<link>). Writes each script to <outdir>/script<N>.mjs
for `node --check`. Usage: python3 -I widget_check.py <html> <outdir>"""
import sys
from html.parser import HTMLParser

VOID = {"meta", "input", "br", "img", "link", "hr", "source", "area", "base", "col", "embed", "track", "wbr"}

class Check(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.errors, self.scripts, self.inputs = [], [], [], []
        self.in_script, self.buf = False, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for bad in ("src", "href"):
            if bad in a:
                self.errors.append(f"<{tag}> has {bad}={a[bad]!r}")
        if tag == "link":
            self.errors.append("<link> element")
        if tag == "input":
            self.inputs.append(a)
        if tag == "script":
            if a.get("type") != "module":
                self.errors.append("script without type=module")
            self.in_script, self.buf = True, []
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag == "script":
            self.scripts.append("".join(self.buf))
            self.in_script = False
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"unbalanced </{tag}> (open: {self.stack})")
        else:
            self.stack.pop()

    def handle_data(self, data):
        if self.in_script:
            self.buf.append(data)
        elif "@import" in data:
            self.errors.append("@import in a style")

html_path, outdir = sys.argv[1], sys.argv[2]
text = open(html_path, encoding="utf-8").read()
c = Check()
c.feed(text)
c.close()
if not text.lower().startswith("<!doctype html>"):
    c.errors.append("no doctype")
if c.stack:
    c.errors.append(f"unclosed elements: {c.stack}")
files = [i for i in c.inputs if i.get("type") == "file"]
if len(files) != 1 or files[0].get("id") != "file":
    c.errors.append(f"expected one <input type=file id=file>, got {files}")
if len(c.scripts) != 2:
    c.errors.append(f"expected 2 inline scripts, got {len(c.scripts)}")
for n, s in enumerate(c.scripts):
    open(f"{outdir}/script{n}.mjs", "w", encoding="utf-8").write(s)
for e in c.errors:
    print("FAIL", e)
print(f"parsed: {len(text)} chars, {len(c.scripts)} scripts, {len(files)} file input")
sys.exit(1 if c.errors else 0)
