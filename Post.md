# `far`

I’ve been building `far`.
It is the shell version of the old IDE “find and replace across files” thing I kept missing.
That operation mattered more than people admit.
You point it at a tree, narrow the files, preview the shape of the change, and then let it go.
That is a real workflow, not a pile of one-off shell glue.

You can glue it together with `find`, `xargs`, and `sed`.
That is not the same thing.
I wanted one command.
One command I could type without rebuilding the pipeline in my head every time.

So `far` is deliberately narrow:
- `fd` finds candidate files
- `rg` filters by content
- [`fsed`](https://github.com/cschladetsch/CppSed) does the replacement

`fsed` is not a footnote.
It is a faster `sed(1)`-style engine in C++23.
Bundling it means one replacement engine, one regex/rewrite model, one thing to document.
That also means fewer weird backend differences and fewer “works here, breaks there” surprises.

```bash
far [OPTIONS] <root> <glob> <find> <replace>
```

That is the whole shape.
Root first. Then the glob. Then the find string. Then the replacement.
If you know those four parts, you know the tool.

Recent work:
- bundled `fsed` instead of relying on system `sed`
- improved capture-group and backreference-friendly replacements
- added a local training playground and demo folder so the workflow can be learned before it hits a real repo
- kept the command shape simple enough that it is actually worth memorizing
- made the playground look like a compact single-screen dashboard instead of a bloated demo page
- kept the repo small enough that the toolchain is still understandable

The goal is straightforward:
make multi-file refactors fast enough to use, safe enough to trust, and simple enough to remember.
That is the point.
Not “clever shell incantation.”
Not “cargo cult one-liner.”
Just a usable command for the thing people already know they want.

In practice, `far` is the workflow and `fsed` is the engine underneath it.
That’s the whole thing.
`far` gets you to the right files.
`fsed` makes the edit path fast enough that you do not hate using it.
The playground exists because if people have to learn the shape once, they should not have to guess at it again.

Images to attach:

- Playground screenshot: https://raw.githubusercontent.com/cschladetsch/ShFar/master/resources/Page1.png

Optional alt text:

- `far` playground: compact single-screen dashboard for teaching the command shape

Repo: https://github.com/cschladetsch/ShFar
