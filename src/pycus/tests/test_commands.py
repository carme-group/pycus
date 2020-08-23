from pycus import commands

from unittest import mock
import unittest
import io
from hamcrest import assert_that, equal_to, contains_exactly, contains_string

from pycus.tests.helper import has_items_in_order


class TestCommands(unittest.TestCase):
    def test_happy_path_add(self):
        runner = mock.MagicMock()
        runner.return_value.returncode = 0
        environment = "/path/to/env"
        name = "an-awesome-env"
        jupyter = "/path/to/jupyter"
        with mock.patch("sys.stdout", new=io.StringIO()) as new_stdout:
            commands.add(environment, name, jupyter, runner)
        output = new_stdout.getvalue().split()
        assert_that(output, has_items_in_order(environment, name, jupyter))
        assert_that(runner.call_count, equal_to(3))
        install, ipykernel, jupyter = runner.call_args_list
        [args], kwargs = install
        assert_that(
            args,
            contains_exactly(
                *"/path/to/env/bin/python -m pip install ipykernel".split()
            ),
        )
        [args], kwargs = ipykernel
        assert_that(
            args,
            contains_exactly(
                *"/path/to/env/bin/python -m ipykernel install "
                "--name an-awesome-env-venv "
                "--display-name an-awesome-env "
                "--prefix /path/to/env".split()
            ),
        )
        [args], kwargs = jupyter
        assert_that(
            args,
            contains_exactly(
                *"/path/to/jupyter kernelspec install "
                "/path/to/env/share/jupyter/kernels/"
                "an-awesome-env-venv --sys-prefix".split()
            ),
        )

    def test_bad_env_add(self):
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
        assert_that(
            lines,
            contains_exactly(
                contains_string("install ipykernel"),
                "Output:",
                runner.return_value.stdout.strip(),
                "Error:",
                runner.return_value.stderr.strip(),
            ),
        )

    def test_happy_path_add_default_name(self):
        runner = mock.MagicMock()
        runner.return_value.returncode = 0
        environment = "/path/to/best-env"
        name = "best-env"
        jupyter = "/path/to/jupyter"
        with mock.patch("sys.stdout", new=io.StringIO()) as new_stdout:
            commands.add(environment, None, jupyter, runner)
        output = new_stdout.getvalue().split()
        assert_that(output, has_items_in_order(environment, "best-env", jupyter))
        assert_that(runner.call_count, equal_to(3))

    def test_happy_path_add_default_name_trailing_slash(self):
        runner = mock.MagicMock()
        runner.return_value.returncode = 0
        environment = "/path/to/best-env/"
        jupyter = "/path/to/jupyter"
        with mock.patch("sys.stdout", new=io.StringIO()) as new_stdout:
            commands.add(environment, None, jupyter, runner)
        output = new_stdout.getvalue().split()
        assert_that(output, has_items_in_order(environment, "best-env", jupyter))
        assert_that(runner.call_count, equal_to(3))

    def test_happy_path_add_default_jupyter(self):
        runner = mock.MagicMock()
        runner.return_value.returncode = 0
        environment = "/path/to/best-env/"
        with mock.patch("sys.stdout", new=io.StringIO()) as new_stdout:
            commands.add(environment, None, None, runner)
        output = new_stdout.getvalue().split()
        assert_that(output, has_items_in_order(environment, "best-env", "jupyter"))
        assert_that(runner.call_count, equal_to(3))
