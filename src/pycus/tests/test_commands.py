# type: ignore
from pycus import commands

from unittest import mock
import unittest
import io
import os
import contextlib
import sys
from hamcrest import (
    assert_that,
    equal_to,
    contains_exactly,
    contains_string,
    all_of,
    not_,
)

import face

from pycus.tests.helper import has_items_in_order, temp_dir


class TestAddd(unittest.TestCase):
    def run(self, result=None):
        with temp_dir() as dirname:
            self.temporary_dir = dirname
            os.mkdir(os.path.join(dirname, "bin"))
            with open(os.path.join(dirname, "bin", "python"), "w"):
                pass
            super().run(result)

    def test_happy_path_add(self):
        runner = mock.MagicMock()
        runner.return_value.returncode = 0
        environment = self.temporary_dir
        name = "an-awesome-env"
        jupyter = "/path/to/jupyter"
        with mock.patch("sys.stdout", new=io.StringIO()) as new_stdout:
            commands.add(environment, name, jupyter, runner, {}, None)
        output = new_stdout.getvalue().split()
        assert_that(output, has_items_in_order(environment, name, jupyter))
        assert_that(runner.call_count, equal_to(3))
        install, ipykernel, jupyter = runner.call_args_list
        [args], kwargs = install
        assert_that(
            args,
            contains_exactly(
                *f"{self.temporary_dir}/bin/python -m pip install ipykernel".split()
            ),
        )
        [args], kwargs = ipykernel
        assert_that(
            args,
            contains_exactly(
                *f"{self.temporary_dir}/bin/python -m ipykernel install "
                "--name an-awesome-env-venv "
                "--display-name an-awesome-env "
                f"--prefix {self.temporary_dir}".split()
            ),
        )
        [args], kwargs = jupyter
        assert_that(
            args,
            contains_exactly(
                *"/path/to/jupyter kernelspec install "
                f"{self.temporary_dir}/share/jupyter/kernels/"
                "an-awesome-env-venv --sys-prefix".split()
            ),
        )

    def test_bad_env_add(self):
        runner = mock.MagicMock(name="runner")
        runner.return_value.returncode = 1
        runner.return_value.stderr = "that environment, it does not exist\n"
        runner.return_value.stdout = "I'm sorry dave, I can't do that\n"
        environment = self.temporary_dir
        name = "an-awesome-env"
        jupyter = "/path/to/jupyter"
        with mock.patch("sys.stdout", new=io.StringIO()) as new_stdout:
            commands.add(environment, name, jupyter, runner, {}, None)
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

    def test_not_running_env_add(self):
        runner = mock.MagicMock(name="runner")
        runner.side_effect = OSError("Cannot run this")
        environment = self.temporary_dir
        name = "an-awesome-env"
        jupyter = "/path/to/jupyter"
        with mock.patch("sys.stdout", new=io.StringIO()) as new_stdout:
            commands.add(environment, name, jupyter, runner, {}, None)
        lines = new_stdout.getvalue().splitlines()
        assert_that(
            lines,
            contains_exactly(
                contains_string("install ipykernel"),
                contains_string("Cannot run this"),
            ),
        )

    def test_not_finding_env(self):
        runner = mock.MagicMock(name="runner")
        runner.side_effect = OSError("Cannot run this")
        environment = os.path.join(self.temporary_dir, "no-such-env")
        with mock.patch("sys.stdout", new=io.StringIO()) as new_stdout:
            commands.add(environment, None, None, runner, {}, None)
        lines = new_stdout.getvalue().splitlines()
        assert_that(
            lines,
            contains_exactly(
                contains_string("no-such-env"),
            ),
        )

    def test_happy_path_add_default_name(self):
        runner = mock.MagicMock()
        runner.return_value.returncode = 0
        environment = self.temporary_dir
        env_name = os.path.basename(self.temporary_dir)
        jupyter = "/path/to/jupyter"
        with mock.patch("sys.stdout", new=io.StringIO()) as new_stdout:
            commands.add(environment, None, jupyter, runner, {}, None)
        output = new_stdout.getvalue().split()
        assert_that(output, has_items_in_order(environment, env_name, jupyter))
        assert_that(runner.call_count, equal_to(3))

    def test_happy_path_add_default_name_trailing_slash(self):
        runner = mock.MagicMock()
        runner.return_value.returncode = 0
        environment = self.temporary_dir + "/"
        env_name = os.path.basename(self.temporary_dir)
        jupyter = "/path/to/jupyter"
        with mock.patch("sys.stdout", new=io.StringIO()) as new_stdout:
            commands.add(environment, None, jupyter, runner, {}, None)
        output = new_stdout.getvalue().split()
        assert_that(output, has_items_in_order(self.temporary_dir, env_name, jupyter))
        assert_that(runner.call_count, equal_to(3))

    def test_happy_path_add_default_jupyter(self):
        runner = mock.MagicMock()
        runner.return_value.returncode = 0
        environment = self.temporary_dir
        env_name = os.path.basename(self.temporary_dir)
        with mock.patch("sys.stdout", new=io.StringIO()) as new_stdout:
            commands.add(environment, None, None, runner, {}, None)
        output = new_stdout.getvalue().split()
        assert_that(output, has_items_in_order(environment, env_name, "jupyter"))
        assert_that(runner.call_count, equal_to(3))

    def test_happy_path_existing_files(self):
        runner = mock.MagicMock()
        runner.return_value.returncode = 0
        with temp_dir() as dirname:
            environment = os.path.join(dirname, "best-env")
            os.makedirs(os.path.join(environment, "bin"))
            with open(os.path.join(environment, "bin", "python"), "w"):
                pass
            with mock.patch("sys.stdout", new=io.StringIO()) as new_stdout:
                commands.add(environment, None, None, runner, {}, None)
        output = new_stdout.getvalue().split()
        assert_that(output, has_items_in_order(environment, "best-env", "jupyter"))
        assert_that(runner.call_count, equal_to(3))

    def test_happy_path_workon_home(self):
        runner = mock.MagicMock()
        runner.return_value.returncode = 0
        with temp_dir() as dirname:
            environment = os.path.join(dirname, "best-env")
            os_environ = dict(WORKON_HOME=dirname)
            os.makedirs(os.path.join(environment, "bin"))
            with open(os.path.join(environment, "bin", "python"), "w"):
                pass
            with mock.patch("sys.stdout", new=io.StringIO()) as new_stdout:
                commands.add("best-env", None, None, runner, os_environ, None)
        output = new_stdout.getvalue().split()
        assert_that(output, has_items_in_order(environment, "best-env", "jupyter"))
        assert_that(runner.call_count, equal_to(3))

    def test_happy_path_workon_home_default_env(self):
        runner = mock.MagicMock()
        runner.return_value.returncode = 0
        with temp_dir() as dirname:
            environment = os.path.join(dirname, "best-env")
            cwd = os.path.join(dirname, "this-doesnt-exist", "best-env")
            os_environ = dict(WORKON_HOME=dirname)
            os.makedirs(os.path.join(environment, "bin"))
            with open(os.path.join(environment, "bin", "python"), "w"):
                pass
            with mock.patch("sys.stdout", new=io.StringIO()) as new_stdout:
                commands.add(None, None, None, runner, os_environ, cwd)
        output = new_stdout.getvalue().split()
        assert_that(output, has_items_in_order(environment, "best-env", "jupyter"))
        assert_that(runner.call_count, equal_to(3))

    def test_no_workon_no_env(self):
        runner = mock.MagicMock()
        runner.return_value.returncode = 0
        with temp_dir() as dirname:
            environment = os.path.join(dirname, "best-env")
            cwd = os.path.join(dirname, "this-doesnt-exist", "best-env")
            os_environ = {}
            os.makedirs(os.path.join(environment, "bin"))
            with open(os.path.join(environment, "bin", "python"), "w"):
                pass
            with mock.patch("sys.stdout", new=io.StringIO()) as new_stdout:
                commands.add(None, None, None, runner, os_environ, cwd)
        lines = new_stdout.getvalue().splitlines()
        assert_that(
            lines,
            contains_exactly(
                contains_string("WORKON_HOME"),
            ),
        )


class TestCreate(unittest.TestCase):
    def run(self, result=None):
        runner = self.runner = mock.MagicMock(name="subprocess.run")

        def venv_maker(args):
            if args[0].endswith("python") and args[1:3] == ["-m", "venv"]:
                environment = args[3]
                os.makedirs(os.path.join(environment, "bin"))
                with open(os.path.join(environment, "bin", "python"), "w"):
                    pass
            return mock.MagicMock(
                name="process_results",
                returncode=0,
                stdout="finished {args}",
                stderr="",
            )

        runner.side_effect = venv_maker
        with contextlib.ExitStack() as stack:
            self.temporary_dir = stack.enter_context(temp_dir())
            self.stdout = stack.enter_context(
                mock.patch(
                    "sys.stdout",
                    new=io.StringIO(),
                )
            )
            super().run(result)

    def test_simple_create(self):
        environment = os.path.join(self.temporary_dir, "newenv")
        commands.create(
            environment=environment,
            python=None,
            runner=self.runner,
            os_environ={},
            current_working_directory=os.path.join(self.temporary_dir, "cwd"),
        )
        call_args_list = list(self.runner.call_args_list)
        [args], kwargs = call_args_list[0]
        assert_that(
            args,
            contains_exactly(*f"{sys.executable} -m venv {environment}".split()),
        )
        assert_that(
            self.stdout.getvalue(),
            all_of(
                contains_string("Added"),
                contains_string(environment),
            ),
        )

    def test_failed_create(self):
        commands.create(
            environment=None,
            python=None,
            runner=self.runner,
            os_environ={},
            current_working_directory=os.path.join(self.temporary_dir, "cwd"),
        )
        assert_that(
            self.runner.call_count,
            equal_to(0),
        )
        assert_that(
            self.stdout.getvalue(),
            all_of(
                not_(contains_string("Added")),
                contains_string("WORKON_HOME"),
            ),
        )

    def test_explicit_python_create(self):
        environment = os.path.join(self.temporary_dir, "newenv")
        commands.create(
            environment=environment,
            python="/very/special/python",
            runner=self.runner,
            os_environ={},
            current_working_directory=os.path.join(self.temporary_dir, "cwd"),
        )
        call_args_list = list(self.runner.call_args_list)
        [args], kwargs = call_args_list[0]
        assert_that(
            args,
            contains_exactly(*f"/very/special/python -m venv {environment}".split()),
        )
        assert_that(
            self.stdout.getvalue(),
            all_of(
                contains_string("Added"),
                contains_string(environment),
            ),
        )

    def test_autodetect_create(self):
        environment = os.path.join(self.temporary_dir, "newenv")
        os_environ = dict(WORKON_HOME=self.temporary_dir)
        current_working_directory = "/home/src/newenv"
        commands.create(
            environment=None,
            python=None,
            runner=self.runner,
            os_environ=os_environ,
            current_working_directory=current_working_directory,
        )
        call_args_list = list(self.runner.call_args_list)
        [args], kwargs = call_args_list[0]
        assert_that(
            args,
            contains_exactly(*f"{sys.executable} -m venv {environment}".split()),
        )
        assert_that(
            self.stdout.getvalue(),
            all_of(
                contains_string("Added"),
                contains_string(environment),
            ),
        )


class TestMakeMiddlewares(unittest.TestCase):
    def test_stringy_middleware(self):
        recorder = mock.MagicMock()

        def silly(silly_string):
            recorder(silly_string)

        static = commands.make_middlewares(silly_string="super silly")
        silly_cmd = face.Command(silly)
        for mw in static.values():
            silly_cmd.add(mw)
        silly_cmd.run(argv=["silly"])
        assert_that(recorder.call_count, equal_to(1))
        [value], kwargs = recorder.call_args
        assert_that(value, equal_to("super silly"))
