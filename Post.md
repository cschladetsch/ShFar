# `far`

I’ve been building `far`, a small CLI for safe batch find-and-replace across a tree of files.

The motivation is simple:

I always missed the old IDE-style “find and replace across files” operation after moving fully back to the shell.

Yes, you can always stitch something together with `find`, `xargs`, and `sed`.
But I wanted one remembered command, one workflow, and one tool I could trust.

So `far` is deliberately narrow:
- `fd` finds the candidate files
- `rg` filters by content
- `fsed` performs the replacement

`fsed` is another tool I’ve been building: a faster `sed(1)`-style engine in C++23.

That gave `far` a clean foundation:
- one replacement engine
- one set of regex/replacement semantics
- one command shape that is easy to remember

```bash
far [OPTIONS] <root> <glob> <find> <replace>
```

Recent work tightened that up a bit:
- bundled `fsed` instead of relying on system `sed`
- improved regex/backreference-friendly replacements
- added a local training playground with a demo folder so the workflow can be learned before it gets used on a real repo

The goal is straightforward:
make multi-file refactors fast enough to use, safe enough to trust, and simple enough to remember.

So [`fsed`](https://github.com/cschladetsch/CppSed) is the engine.
`far` is the workflow wrapped around it.

Images to attach:

- Playground screenshot: https://raw.githubusercontent.com/cschladetsch/ShFar/master/resources/Page1.png

Optional alt text:

- `far` playground: compact single-screen dashboard for teaching the command shape

Repo: <PRIVATE_URL>
