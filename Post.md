# `far`

I’ve been working on `far`, a small CLI for safe batch find-and-replace across a tree of files.

It sits on top of another tool I’ve been building, `fsed`, a fast `sed(1)`-style engine in C++23.

The idea is narrow:
- `fd` to find candidate files
- `rg` to filter by content
- `fsed` to do the actual replacement
- one command shape that is easy to remember

The workflow is the point:

```bash
far [OPTIONS] <root> <glob> <find> <replace>
```

So instead of stitching together ad hoc shell pipelines every time, I can type one command, preview it with `-n`, keep backups with `-b`, and run it with less friction.

Recent work tightened that up a bit:
- bundled `fsed` instead of relying on system `sed`
- added regex/backreference-friendly replacements
- added a local playground with a demo folder so the command can be learned before it gets used on a real repo

The goal is simple: make multi-file refactors fast enough to use, safe enough to trust, and simple enough to remember.

So `fsed` is the engine, and `far` is the workflow wrapped around it.

Repo: <PRIVATE_URL>
