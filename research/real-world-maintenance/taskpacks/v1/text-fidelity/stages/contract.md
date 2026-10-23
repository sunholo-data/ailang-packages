# Frozen development contract: text fidelity v1

Frozen before native references, 2026-10-23. Adapted from Calamine #671/#673's
logical-text regression. This is a bounded cell-text consumer, not an XLSX/XML
parser port. The upstream producer has already decoded character references.
Both languages receive identical supplied JSON producers and own all text
assembly, trimming, event validation and output construction below.

Each CLI reads one JSON file containing an array of cell requests and prints
one JSON array, retaining order. Invalid cell data yields a result record,
not a crash. The basic record has exactly cell, ok, text, error. On error text
is null and error is invalid_cell. Successful empty text is ok=true, text="".
All input fields are required and typed; unknown schema or event kind is invalid.
Fixture files and independently handwritten expected outputs were written before
implementations. No fixture is a secret holdout; all are development controls.

Baseline cell.text/1: cell:string, preserve:bool, invalid:bool, text:string.
Retain all logical characters, including leading/trailing whitespace. No edge
trimming has yet been requested. invalid=true returns invalid_cell.

S1 cell.text/1: introduce default edge-ASCII trimming. With preserve=true retain
all text. Otherwise trim only U+0009..U+000D and U+0020 at the edges of the complete
logical cell. Never collapse internal spaces or strip non-ASCII whitespace.
All existing error and consumer-record obligations remain.

S2 cell.events/2: upstream interface replaces text with events, an ordered array
of records {kind:string,value:string,style:string}. Legal kinds are text,
reference and error. Reference value is already decoded (including a literal
space or non-ASCII character); concatenate all text/reference values before
applying S1 policy once. An error event makes the entire cell invalid. Chunk
boundaries cannot alter semantics. style must be present but is not interpreted.

S3 cell.events/3: legal events additionally include cdata and run. Treat their
value as literal logical text, never entity-decode it a second time. Retain the
basic record. Add characters (Unicode scalar count of final text; null on error)
and parts (ordered records {kind,text,style} for all text-bearing events, before
edge trimming; empty on error). Preserve style for run, use an empty style for
other kinds. Empty event streams are valid empty cells. The JSON transport uses
Unicode scalar strings; unpaired surrogates are outside this task contract.

Allowed native dependencies: AILANG std/json/string/list/result/option and
FS/Env/IO transport; Python standard-library json and Unicode strings. No target
implementation may call the other language or consume expected-output fixtures.
Native reference checkpoints may share a qualification library, but the supplied
baseline starter contains no future-stage solution or mutant policy.
