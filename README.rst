flexible-vrp
**************

Project structure
===================

- documentation: project documentation in LaTeX.
- data: input and solution data.
- exploitation_tools: directory with tools functions used to exploit the solution.
- flexible_vrp: source code of the application.

  + core: directory with the main classes of the app.
  + schemas: directory with jsonschemas for the instance, configuration and solution.
  + solvers: directory with the solving methods.
  + test: directory with tests.
  + test_data: directory with small instances and solutions in json used for testing purpose.
  + tools: directory with generic tools functions used in the project

- main.py : main script to solve the problem with a chosen method.
- requirements.txt: list of libraries to install.

Useful commands
======================

Install requirements
^^^^^^^^^^^^^^^^^^^^^^

``pip install -r requirements.txt``

Launch tests
^^^^^^^^^^^^^^

