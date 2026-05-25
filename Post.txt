Building far: Bringing IDE-Grade Find & Replace to the Terminal

We've all been there: you need to rename a class, refactor an API, or update config values across dozens of files in your repository. 

Traditionally, this meant constructing a brittle, stressful shell pipeline:
find . -name "*.cpp" -print0 | xargs -0 sed -i 's/OldClass/NewClass/g'

Make one regex typo, and it can quietly corrupt your entire project directory. Even worse, macOS (BSD sed) and Linux (GNU sed) behave differently, making these commands highly error-prone in cross-platform CI pipelines.

I wanted something better. A single, fast, safe terminal command that acts like an IDE’s "Find and Replace across Files" dialog.

So, I built far (Find and Replace). 

far is a high-efficiency CLI tool that acts as an orchestrator, wiring together three best-in-class tools to solve this problem:

1. fd: Traverses the filesystem with extreme parallel speed to discover candidate files.
2. ripgrep (rg): Filters those files instantly using the fastest pattern search engine in existence.
3. fsed: A native, compiler-grade C++23 stream editor clone I built from scratch (CppSed).

By bundling fsed directly, far guarantees 100% consistent regex, capture group, and case-conversion behavior on macOS, Linux, and Windows. No more platform guessing, and no more "works on my machine, breaks in CI" surprises.

Built for Safety and Developer Experience (UX):
*   Interactive by Default: It prompts you with a list of target files and matching lines before writing a single byte.
*   Dry Runs (-n): Preview matches and planned substitutions safely without making changes.
*   Automatic Backups (-b): Generates .bak files automatically so you always have a rollback path.
*   Visual Training Playground: Running ./teach boots up a local single-screen web dashboard allowing you to experiment with glob patterns and regex operations safely in a sandbox folder.

It has been an incredibly fun exercise in combining low-level systems engineering (C++23 jump-flattening compiler architectures and memory-mapped zero-copy I/O) with practical terminal UX.

Check out the code, architecture diagrams, and guidelines on GitHub:

far (CLI Orchestrator): https://github.com/cschladetsch/ShFar
fsed (C++23 Stream Engine): https://github.com/cschladetsch/CppSed

#programming #cpp #devops #systems #git #refactoring #opensource #cli #developerproductivity
