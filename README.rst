Yorkshire
---------

🐶 Yorkshire is your friend; Yorkshire checks Python's requirements files for a
possible dependency confusion.

Note if `PEP-708: Extending the Repository API to Mitigate Dependency Confusion
Attacks
<https://discuss.python.org/t/pep-708-extending-the-repository-api-to-mitigate-dependency-confusion-attacks/24179>`__
gets accepted, you do not need to use Yorkshire anymore.

The tool checks whether there are configured any extra index URLs in
corresponding files. Currently, there are supported the following installation
methods and their files:

* `PDM <https://pdm.fming.dev/>`__ - ``pyproject.toml`` and ``pdm.lock``
* `Pipenv <https://pipenv.pypa.io/en/latest/>`__ - ``Pipfile`` and ``Pipfile.lock``
* `Poetry <https://python-poetry.org/>`__ - ``pyproject.toml`` (poetry.lock is not sufficient for a dependency confusion detection)
* `pip <https://pypi.org/project/pip/>`__ - raw ``requirements.txt``
* `pip-tools <https://pypi.org/project/pip-tools/>`__ - ``requirements.txt`` and ``requirements.in``
* `setup.cfg <https://setuptools.pypa.io/en/latest/userguide/declarative_config.html>`__ - the tool parses setuptool's ``setup.cfg`` configuration
* `setup.py <https://setuptools.pypa.io/>`__ - the tool statically analyzes sources of the ``setup.py`` script

Installation
============

Yorkshire is available on PyPI:

.. code-block:: console

  pip install yorkshire
  yorkshire --help

To install the tool from this Git repository, issue the following command from
the root of the ``yorkshire`` directory:

.. code-block:: console

  python3 -m venv venv
  source venv/bin/activate
  pip install -e .
  yorkshire --help

Usage
=====

.. code-block:: console

  yorkshire detect DIR|FILE|URL

* if the argument supplied is a directory, Yorkshire traverses the whole
  directory tree and checks files present
* if the argument supplied is a file, Yorkshire performs analysis on the given
  file
* if the argument supplied is URL, Yorksire downloads the referenced file and
  perfoms analysis (the file is deleted as the analysis finishes)

See ``--help`` for more information:

.. code-block:: console

  yorkshire --help

  yorkshire detect --help

License
=======

See the LICENSE file.
