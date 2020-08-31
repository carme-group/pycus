from __future__ import annotations

import functools
import os
import subprocess
import sys

import face
from typing import Sequence, Any, Mapping, Callable
from typing_extensions import Protocol


class _ProcessHopesShattered(Exception):
    pass


class _CompletedProcess(Protocol):
    returncode: int
    stdout: str
    stderr: str


class _Runner(Protocol):
    def __call__(self, args: Sequence[str]) -> _CompletedProcess:
        "Run"


def _optimistic_run(
    runner: _Runner,
    description: str,
    arguments: Sequence[str],
) -> None:
    try:
        result = runner(arguments)
    except OSError as exc:
        exc.description = description
        raise
    if result.returncode != 0:
        raise _ProcessHopesShattered(description, result)


def add(
    environment: str,
    name: str,
    jupyter: str,
    runner: _Runner,
    os_environ: Mapping[str, str],
) -> None:
    """
    Add a virtual environment
    """
    if not os.path.exists(environment):
        environment = os.path.join(os_environ.get("WORKON_HOME", ""), environment)
    if name is None:
        name = os.path.basename(environment)
        if name == "":  # Allow trailing / because of shell completion
            name = os.path.basename(os.path.dirname(environment))
    if jupyter is None:
        jupyter = "jupyter"
    venv_python = os.path.join(environment, "bin", "python")
    try:
        _optimistic_run(
            runner,
            "install ipykernel",
            [venv_python, "-m", "pip", "install", "ipykernel"],
        )
        logical_name = f"{name}-venv"
        _optimistic_run(
            runner,
            "create ipykernel description",
            [
                venv_python,
                "-m",
                "ipykernel",
                "install",
                "--name",
                logical_name,
                "--display-name",
                name,
                "--prefix",
                environment,
            ],
        )
        description = os.path.join(
            environment, "share", "jupyter", "kernels", logical_name
        )
        _optimistic_run(
            runner,
            "add ipykernel description to jupyter",
            [jupyter, "kernelspec", "install", description, "--sys-prefix"],
        )
    except _ProcessHopesShattered as exc:
        stage, details = exc.args
        print(f"Commands to {stage} failed:")
        print("Output:")
        sys.stdout.write(details.stdout)
        print("Error:")
        sys.stdout.write(details.stderr)
    except OSError as exc:
        print(f"Commands to {exc.description} failed:")
        print(exc)
    else:
        print(f"✅ Added {environment} as {name} to {jupyter}")


class _Middleware(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> _Middleware:
        "next"


def make_middlewares(**kwargs: Any) -> Mapping[str, Callable]:
    def make_middleware(name: str, thing: Any) -> Callable:
        @face.face_middleware(provides=[name])
        def middleware(next_: _Middleware) -> _Middleware:
            return next_(**{name: thing})

        return middleware

    ret_value = {}
    for key, value in kwargs.items():
        ret_value[key] = make_middleware(key, value)
    return ret_value


STATIC_MIDDLEWARES = make_middlewares(
    runner=functools.partial(subprocess.run, capture_output=True, text=True),
    os_environ=os.environ,
)

add_cmd = face.Command(add)
for mw in STATIC_MIDDLEWARES.values():
    add_cmd.add(mw)
add_cmd.add("--environment", missing=face.ERROR)
add_cmd.add("--jupyter")
add_cmd.add("--name")


def _need_subcommand() -> None:  # pragma: no cover
    raise face.UsageError("missing subcommand")


main_command = face.Command(_need_subcommand, name="pycus")
main_command.add(add_cmd)
