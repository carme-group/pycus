import functools
import os
import subprocess

import face

class ProcessHopesShattered(Exception):
    pass


def optimistic_run(runner, description, arguments):
    result = runner(arguments)
    if result.returncode != 0:
        raise ProcessHopesShattered(description, result)


def add(environment, name, jupyter, runner):
    """
    Add a virtual environment
    """
    if name is None:
        name = os.path.basename(environment)
        if name == "": # Allow trailing / because of shell completion
            name = os.path.basename(os.path.dirname(environment))
    if jupyter is None:
        jupyter = "jupyter"
    venv_python = os.path.join(environment, "bin", "python")
    try:
        optimistic_run(runner, "install ipykernel",
                       [venv_python, "-m", "pip", "install", "ipykernel"])
        logical_name = f"{name}-venv"
        optimistic_run(runner, "create ipykernel description",
                       [venv_python, "-m", "ipykernel", "install",
                                     "--name", logical_name,
                                     "--display-name", name,
                                     "--prefix", environment])
        description = os.path.join(environment, "share", "jupyter", "kernels",
                                   logical_name)
        optimistic_run(runner, "add ipykernel description to jupyter",
                       [jupyter, "kernelspec", "install", description,
                        "--sys-prefix",])
    except ProcessHopesShattered as exc:
        stage, details = exc.args
        print("Commands to f{stage} failed:")
        print("Output:")
        sys.stdout.write(details.stdout)
        print("Error:")
        sys.stdout.write(details.stderr)
    print(f"✅ added {environment} as {name} to {jupyter}")


@face.face_middleware(provides=['runner'])
def runner_mw(next_):
    return next_(runner=functools.partial(subprocess.run, capture_output=True, text=True))

add_cmd = face.Command(add)
add_cmd.add(runner_mw)
add_cmd.add("--environment", missing=face.ERROR)
add_cmd.add("--jupyter")
add_cmd.add("--name")

def need_subcommand():
    raise face.UsageError("missing subcommand")

main_command = face.Command(need_subcommand, name="picus")
main_command.add(add_cmd)
