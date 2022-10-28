flexible-vrp
**************

Project structure
===================

- **analysis_tools:** directory with tools functions used to analyse the solution.
- **data:** input and solution data.
- **documentation:** project documentation in LaTeX.
- **flexible_vrp:** source code of the application.

  + **core:** directory with the main classes of the app.
  + **schemas:** directory with jsonschemas for the instance, configuration and solution.
  + **solvers:** directory with the solving methods.
  + **test:** directory with tests.

    + **test_data:** directory with small instances and solutions in json used for testing purpose.
  + **tools:** directory with generic tools functions used in the project

- *main.py:* main script to solve the problem with a chosen method.
- *requirements.txt:* list of libraries to install.

Useful commands
======================
The following commands should be launched in pycharm terminal from the root folder ("flexible-vrp")

Set up virtual environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Create the virtual environment::

    py -m venv ./venv/

Activate the virtual environment::

    venv\Scripts\activate

Install requirements (see next)

Install library
^^^^^^^^^^^^^^^^^^
::

    pip install library_name

Install requirements
^^^^^^^^^^^^^^^^^^^^^^
::

    pip install -r requirements.txt

Reformat code with black
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Reformat a file or folder::

    black folder_name

Reformat the entire project::

    black .

In order to prevent black from reformatting some code, add the following comments in the file::

    # fmt: off
    your code
    # fmt: on


Launch tests
^^^^^^^^^^^^^^
::

    py -m unittest

