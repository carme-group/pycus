from __future__ import annotations

import os
import sys
import contextlib

import attrs

import gather
from gather import commands
from gather.commands import add_argument


_COMMANDS_COLLECTOR = gather.Collector()
REGISTER = commands.make_command_register(_COMMANDS_COLLECTOR)

def main(): # pragma: no cover
    commands.run(
        parser=commands.set_parser(
            collected=_COMMANDS_COLLECTOR.collect()
        )
    )


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
        result = runner(
            arguments,
            capture_output=True,
            text=True,
            check=True,
        )
    except OSError as exc:
        args = list(exc.args)
        args.append(description)
        exc.args = tuple(args)
        raise
    if result.returncode != 0:
        raise _ProcessHopesShattered(description, result)


def _get_environment(
    os_environ: Mapping[str, str],
    dirname: Optional[str],
) -> str:
    attempts = []
    if dirname is None:
        dirname = os.path.basename(os_environ["PWD"])
    else:
        attempts.append(os.path.abspath(dirname))
    with contextlib.suppress(KeyError):
        attempts.append(os.path.join(os_environ["WORKON_HOME"], dirname))
    for attempt in attempts:
        python = os.path.join(attempt, "bin", "python")
        if os.path.exists(python):
            return attempt
    raise ValueError("Cannot find environment, tried", attempts)


@contextlib.contextmanager
def _user_friendly_errors() -> Iterator[None]:
    try:
        yield
    except _ProcessHopesShattered as exc:
        stage, details = exc.args
        print(f"Commands to {stage} failed:")
        print("Output:")
        sys.stdout.write(str(details.stdout))
        print("Error:")
        sys.stdout.write(str(details.stderr))
    except OSError as exc:
        print(f"Commands to {exc.args[-1]} failed:")
        print(exc)
    except ValueError as exc:
        string_exc = " ".join(map(str, exc.args))
        print(f"Could not add environment: {string_exc}")
    else:
        return
    raise SystemExit(1)


@REGISTER(
    add_argument("--environment"),
    add_argument("--python", default=sys.executable),
    add_argument("--jupyter-python", default=sys.executable),
)
def create(
    *,
    args,
    env,
    sp_run,
f) -> None:
    with _user_friendly_errors():
        if args.environment is None:
            args.environment = os.path.basename(env["PWD"])
        if not os.path.isabs(environment):
            if "WORKON_HOME" not in env:
                raise ValueError("not absolute path and no WORKON_HOME", args.environment)
            args.environment = os.path.join(env["WORKON_HOME"], args.environment)
        _optimistic_run(
            sp_run,
            "create environment",
            [python, "-m", "venv", environment],
        )
    add(
        args=args,
        env=env,
        sp_run=sp_run,
    )


@REGISTER(
    add_argument("--environment"),
    add_argument("--jupyter-python", default=sys.executable),
)
def add(
    *,
    args,
    env,
    sp_run,
) -> None:
    """
    Add a virtual environment
    """
    with _user_friendly_errors():
        args.environment = _get_environment(
            env, args.environment,
        )
        if args.name is None:
            args.name = os.path.basename(args.environment)
        venv_python = os.path.join(args.environment, "bin", "python")
        logical_name = f"{name}-venv"
        description = os.path.join(
            args.environment, "share", "jupyter", "kernels", logical_name
        )
        _optimistic_run(
            sp_run,
            "install ipykernel",
            [venv_python, "-m", "pip", "install", "ipykernel"],
        )
        _optimistic_run(
            sp_run,
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
        _optimistic_run(
            sp_run,
            "add ipykernel description to jupyter",
            [
                args.jupyter_python,
                "-m", 
                "jupyter",
                "kernelspec",
                "install",
                description,
                "--sys-prefix"
            ],
        )
    print(f"✅ Added {environment} as {name} to {jupyter}")
