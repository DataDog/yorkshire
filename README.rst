Yorkshire
---------

🐶 Yorkshire is your friend; Yorkshire checks Python's requirements files for a
possible dependency confusion.

Note if `PEP-708: Extending the Repository API to Mitigate Dependency Confusion
Attacks
<https://discuss.python.org/t/pep-708-extending-the-repository-api-to-mitigate-dependency-confusion-attacks/24179>`__
gets accepted, you do not need to use Yorkshire anymore.

Yorkshire was developed to perform scans on all the possible files that can
manipulate with Python package index configuration. The scan will reveal
configuration of multiple Python package indexes to check for a possible
dependency confusion. By reviewing results, users can prevent from issues like
the one with `PyTorch's torchvision
<https://pytorch.org/blog/compromised-nightly-dependency/>`__.  The tool does
not report whether there is an actual dependency confusion (that would require
more in-depth analysis), but whether there is a possibility for a dependency
confusion - whether packages could be consumed from multiple Python package
indexes.

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

Example Run
===========

The tool can be run on a single requirements file and check Python package indexes configured:

.. code-block:: console

  $ yorkshire detect tests/data/requirements_files/fail/pipfile/Pipfile
  2023-03-10 14:07:01,640 [24252] INFO     yorkshire._lib: Performing detection in Pipfile file located at 'tests/data/requirements_files/fail/pipfile'
  2023-03-10 14:07:01,640 [24252] WARNING  yorkshire._lib: File 'tests/data/requirements_files/fail/pipfile/Pipfile' states one or multiple Python package indexes: ['https://pypi.org/simple', 'https://download.pytorch.org/whl/cpu']

Or, it can traverse a directory tree and report findings:

.. code-block:: console

  $ yorkshire detect tests/data/requirements_files/fail
  2023-03-10 14:08:39,811 [24502] INFO     yorkshire._lib: Performing detection in setup.py file located at 'tests/data/requirements_files/fail/setup_py'
  2023-03-10 14:08:39,811 [24502] WARNING  yorkshire._lib: File 'tests/data/requirements_files/fail/setup_py/setup.py' uses dependency links
  2023-03-10 14:08:39,811 [24502] INFO     yorkshire._lib: Performing detection in pyproject.toml file located at 'tests/data/requirements_files/fail/pyproject_toml/poetry'
  2023-03-10 14:08:39,811 [24502] WARNING  yorkshire._lib: File 'tests/data/requirements_files/fail/pyproject_toml/poetry/pyproject.toml' uses an explicitly configured Poetry source: ['https://test.pypi.org/simple/']
  2023-03-10 14:08:39,811 [24502] INFO     yorkshire._lib: Performing detection in pyproject.toml file located at 'tests/data/requirements_files/fail/pyproject_toml/pdm'
  2023-03-10 14:08:39,811 [24502] WARNING  yorkshire._lib: File 'tests/data/requirements_files/fail/pyproject_toml/pdm/pyproject.toml' uses an explicitly configured PDM source: ['https://test.pypi.org/simple']
  2023-03-10 14:08:39,811 [24502] INFO     yorkshire._lib: Performing detection in setup.cfg file located at 'tests/data/requirements_files/fail/setup_cfg/01'
  2023-03-10 14:08:39,811 [24502] WARNING  yorkshire._lib: File 'tests/data/requirements_files/fail/setup_cfg/01/setup.cfg' uses dependency links: http://peak.telecommunity.com/snapshots/
  2023-03-10 14:08:39,812 [24502] INFO     yorkshire._lib: Performing detection in requirements.in file located at 'tests/data/requirements_files/fail/requirements/02'
  2023-03-10 14:08:39,812 [24502] WARNING  yorkshire._lib: File 'tests/data/requirements_files/fail/requirements/02/requirements.in' states one or multiple extra index URLs: ['https://download.pytorch.org/whl/cpu']
  2023-03-10 14:08:39,812 [24502] INFO     yorkshire._lib: Performing detection in requirements.in file located at 'tests/data/requirements_files/fail/requirements/01'
  2023-03-10 14:08:39,812 [24502] WARNING  yorkshire._lib: File 'tests/data/requirements_files/fail/requirements/01/requirements.in' states --find-links: ['https://github.com/NVIDIA/Torch-TensorRT/releases']
  2023-03-10 14:08:39,813 [24502] INFO     yorkshire._lib: Performing detection in pdm.lock file located at 'tests/data/requirements_files/fail/pdm_lock'
  2023-03-10 14:08:39,813 [24502] WARNING  yorkshire._lib: Package 'certifi 2021.10.8' is not consumed from PyPI: https://files.custom.org/packages/37/45/946c02767aabb873146011e665728b680884cd8fe70dde973c640e45b775/certifi-2021.10.8-py2.py3-none-any.whl
  2023-03-10 14:08:39,813 [24502] INFO     yorkshire._lib: Performing detection in Pipfile file located at 'tests/data/requirements_files/fail/pipfile'
  2023-03-10 14:08:39,813 [24502] WARNING  yorkshire._lib: File 'tests/data/requirements_files/fail/pipfile/Pipfile' states one or multiple Python package indexes: ['https://pypi.org/simple', 'https://download.pytorch.org/whl/cpu']
  2023-03-10 14:08:39,813 [24502] INFO     yorkshire._lib: Performing detection in Pipfile.lock file located at 'tests/data/requirements_files/fail/pipfile_lock'
  2023-03-10 14:08:39,813 [24502] WARNING  yorkshire._lib: File 'tests/data/requirements_files/fail/pipfile_lock/Pipfile.lock' states one or multiple Python package indexes: ['https://pypi.org/simple', 'https://localhost:8080/simple']

The tool can also check a file referenced by URL (any query parameters are intentionally discarded):

.. code-block:: console

  $ yorkshire detect https://raw.githubusercontent.com/pytorch/pytorch/master/requirements.txt
  2023-03-10 14:11:45,774 [24832] INFO     yorkshire._lib: Performing detection in requirements.txt file located at 'https://raw.githubusercontent.com/pytorch/pytorch/master'
  $ echo $?
  0

Using as Yorkshire as a library
===============================

Yorkshire can be used as a library in your application:

.. code-block:: python

  >>> import yorkshire
  >>> path = os.getcwd()
  >>> yorkshire.detect(path)
  >>> yorkshire.detect_file(path)
  >>> help(yorkshire.detect)
  >>> help(yorkshire.detect_file)

License
=======

See the LICENSE file.
