# Dapy: Distributed Algorithms in Python

<p style="font-style:italic">
IMPORTANT:
This project is in a very early stage of development; use at your own risks.
</p>

## Description

This is a simple (simplistic) programming framework to simulate the execution of distributed algorithms.



## How to begin

The project is currently under active development with many changes to come in the near future.
Therefore, it is not yet recommended to install it as a fixed module.

### Requirements

It is recommended to use [uv](https://docs.astral.sh/uv/) for dependency management and building.
The project requires Python 3.13 or higher which is installed in a virtual environment by `uv` automatically _(i.e., you have nothing to do if using `uv`)_.

### Setup: Initial steps

To use the environment, please follow the following steps:

1. Clone this repository.
2. Install `uv` if you haven't already:
    ```shell
    brew install uv # on Mac
    ```
    _check the page ["Installing uv"](https://docs.astral.sh/uv/getting-started/installation/) for other environments._
    
3. Synchronize dependencies (omit `--all-groups` for a more lightweight install):
    ```shell
    uv sync --all-groups
    ```
4. Check if the install worked properly by running an example:
    ```shell
    uv run python examples/example.py
    ```
    The output should show some execution trace of the "Learn the Topology" algorithm in a ring of four processes.

### Getting Started

Look at the two parts annotated example that explains:
* [How to write an algorithm](docs/sample-algorithm.md)
* [How to define an execution](docs/sample-execution.md)

You can also check the following code template:
* [`examples/template.py`](examples/template.py)

### Optional dependencies

Some additional features are available optionally:

* `json` enables serialization/deserialization of `Trace` objects to/from JSON strings using the `dump_json()` and `load_json()` methods.

To use optional features in a user installation, install `dapy` with the optional dependencies:
```shell
uv pip install -e ".[json]"
```

**Note**: During development, the `json` dependency is included in the dev group, so `uv sync --all-groups` will automatically install it for testing.

### Development

To contribute to the project:

1. Sync all dependencies including dev tools:
    ```shell
    uv sync --all-groups
    ```

2. Run tests:
    ```shell
    uv run pytest
    ```

3. Run linting and formatting:
    ```shell
    uv run ruff check src --fix
    uv run ruff format src
    ```

4. Install pre-commit hooks:
    ```shell
    uv pip install pre-commit
    pre-commit install
    ```
