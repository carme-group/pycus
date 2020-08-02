from pycus import commands

from unittest import mock
import io


def test_happy_path_add():
    runner = mock.MagicMock()
    runner.return_value.returncode = 0
    environment = "/path/to/env"
    name = "an-awesome-env"
    jupyter = "/path/to/jupyter"
    with mock.patch("sys.stdout", new=io.StringIO()) as new_stdout:
        commands.add(environment, name, jupyter, runner)
    output = new_stdout.getvalue().split()
    assert environment in output
    assert name in output[output.index(environment) :]
    assert jupyter in output[output.index(name) :]
    assert len(runner.call_args_list) == 3
    install, ipykernel, jupyter = runner.call_args_list
    [args], kwargs = install
    assert " ".join(args) == "/path/to/env/bin/python -m pip install ipykernel"
    [args], kwargs = ipykernel
    assert " ".join(args) == (
        "/path/to/env/bin/python -m ipykernel install "
        "--name an-awesome-env-venv "
        "--display-name an-awesome-env "
        "--prefix /path/to/env"
    )
    [args], kwargs = jupyter
    assert " ".join(args) == (
        "/path/to/jupyter kernelspec install "
        "/path/to/env/share/jupyter/kernels/"
        "an-awesome-env-venv --sys-prefix"
    )


def test_bad_env_add():
    runner = mock.MagicMock(name="runner")
    runner.return_value.returncode = 1
    runner.return_value.stderr = "that environment, it does not exist\n"
    runner.return_value.stdout = "I'm sorry dave, I can't do that\n"
    environment = "/path/to/env"
    name = "an-awesome-env"
    jupyter = "/path/to/jupyter"
    with mock.patch("sys.stdout", new=io.StringIO()) as new_stdout:
        commands.add(environment, name, jupyter, runner)
    lines = new_stdout.getvalue().splitlines()
    assert "install ipykernel" in lines.pop(0)
    assert "Output:" == lines.pop(0)
    assert runner.return_value.stdout.strip() == lines.pop(0)
    assert "Error:" == lines.pop(0)
    assert runner.return_value.stderr.strip() == lines.pop(0)
    assert lines == []


def test_happy_path_add_default_name():
    runner = mock.MagicMock()
    runner.return_value.returncode = 0
    environment = "/path/to/best-env"
    name = "best-env"
    jupyter = "/path/to/jupyter"
    with mock.patch("sys.stdout", new=io.StringIO()) as new_stdout:
        commands.add(environment, None, jupyter, runner)
    output = new_stdout.getvalue().split()
    assert environment in output
    assert name in output[output.index(environment) :]
    assert jupyter in output[output.index(name) :]
    assert len(runner.call_args_list) == 3


def test_happy_path_add_default_name_trailing_slash():
    runner = mock.MagicMock()
    runner.return_value.returncode = 0
    environment = "/path/to/best-env/"
    name = "best-env"
    jupyter = "/path/to/jupyter"
    with mock.patch("sys.stdout", new=io.StringIO()) as new_stdout:
        commands.add(environment, None, jupyter, runner)
    output = new_stdout.getvalue().split()
    assert environment in output
    assert name in output[output.index(environment) :]
    assert jupyter in output[output.index(name) :]
    assert len(runner.call_args_list) == 3


def test_happy_path_add_default_jupyter():
    runner = mock.MagicMock()
    runner.return_value.returncode = 0
    environment = "/path/to/best-env/"
    name = "best-env"
    jupyter = "jupyter"
    with mock.patch("sys.stdout", new=io.StringIO()) as new_stdout:
        commands.add(environment, None, None, runner)
    output = new_stdout.getvalue().split()
    assert environment in output
    assert name in output[output.index(environment) :]
    assert jupyter in output[output.index(name) :]
    assert len(runner.call_args_list) == 3
