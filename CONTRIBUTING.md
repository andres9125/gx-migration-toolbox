# Contributing

Contributions are welcome.

Keep all code, documentation, fixtures, paths, and command output generic and
in English. Do not submit customer names, source exports, credentials, internal
URLs, proprietary package contents, or real reports.

Before opening a pull request, run:

~~~powershell
python -m unittest discover -s tests -v
python -m compileall -q src
~~~

Use synthetic source snippets in tests. Changes must preserve the tool's
read-only behavior: it may inspect files but must not modify or execute them.
