import functools
import os
import subprocess
import sys

import face


class _ProcessHopesShattered(Exception):
    pass


def _optimistic_run(runner, description, arguments):
    result = runner(arguments)
    if result.returncode != 0:
        raise _ProcessHopesShattered(description, result)


def add(environment, name, jupyter, runner):
    """
    Add a virtual environment
    """
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
    else:
        print(f"✅ Added {environment} as {name} to {jupyter}")


@face.face_middleware(provides=["runner"])
def runner_mw(next_):  # pragma: no cover
    return next_(
        runner=functools.partial(subprocess.run, capture_output=True, text=True)
    )


add_cmd = face.Command(add)
add_cmd.add(runner_mw)
add_cmd.add("--environment", missing=face.ERROR)
add_cmd.add("--jupyter")
add_cmd.add("--name")


def _need_subcommand():  # pragma: no cover
    raise face.UsageError("missing subcommand")


main_command = face.Command(_need_subcommand, name="pycus")
main_command.add(add_cmd)
