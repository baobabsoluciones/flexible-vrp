flexible-vrp
**************

Project structure
===================

- analysis_tools: directory with tools functions used to analyse the solution.
- data: input and solution data.
- documentation: project documentation in LaTeX.
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

