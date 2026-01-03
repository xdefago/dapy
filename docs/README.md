## Generate API Documentation

Install pdoc (included in `dev` dependencies):
```shell
uv pip install pdoc
```

Generate the docs:
```shell
uv run pdoc -o docs/api -d google src/dapy
```

Open the docs (using open command on Mac terminal):
```shell
open docs/api/index.html
```
