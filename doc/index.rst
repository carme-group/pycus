Pycus
=====

Jupyter supports running with multiple kernels.
Unfortunately, adding a virtual environment to Jupyter is not easy.
Pycus tries to take the pain out of it, making it painless to add environments.

Installation
------------

Install :code:`pycus` in the same environment as Jupyter:


.. code::

    $ pip install pycus

This will add a :code:`pycus` subcommand to Jupyter.

Running
-------

.. code::

    $ jupyter pycus add [--environment <ENVIRONMENT>]

will add the environment.

The :code:`ENVIRONMENT` can be:

* A full path to a virtual environment
* The name of a :code:`virtualenvwrapper` environment
* Empty, in which case it will be equivalent to the :code:`virtualenvwrapper`
  environment with the same name as the current working directory's base name.
  This matches the behavior of :code:`workon .`.

After adding the environment, refresh your JupyterLab browser window,
and you should see the new environment as an option in the launcher window.
