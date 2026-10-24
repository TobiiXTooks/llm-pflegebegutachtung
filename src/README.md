# PflegeBench source tools

The files in this folder are the existing tool implementations. They are now launched through the cross-platform workflow package in `src/pflegebench/`.

Prefer these commands from the project root:

```bash
python -m pflegebench gui-benchmark
python -m pflegebench gui-editor
python -m pflegebench compare-folder
python -m pflegebench dashboard
```

Do not start scripts through OS-specific shell wrappers. The workflow layer handles paths and subprocesses portably.
