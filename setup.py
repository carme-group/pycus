import setuptools

with open("README.rst") as fp:
    long_description = fp.read()

setuptools.setup(
    name="pycus",
    license="MIT",
    description="",
    long_description=long_description,
    use_incremental=True,
    setup_requires=["incremental"],
    author="Moshe Zadka",
    author_email="moshez@zadka.club",
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["incremental", "jupyterlab", "face", "typing_extensions"],
    extras_require=dict(
        test=["virtue", "pyhamcrest", "coverage"],
        lint=["black", "flake8", "mypy", "bandit"],
        doc=["sphinx"],
    ),
    entry_points=dict(
        console_scripts=["jupyter-pycus=pycus.commands:main_command.run"],
    ),
)
