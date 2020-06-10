import os
import pkgutil
import importlib
import unittest
from invoke import task

VENV_ACTIVATE = "venv\\Scripts\\activate" if os.name == 'nt' else ". ./venv/bin/activate"


@task
def collect(c, state):  # pylint: disable=unused-argument,invalid-name
  states_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'states')
  all_states = [name for _, name, _ in pkgutil.iter_modules([states_path])]

  if state == 'all':
    state_names = all_states
  elif state in all_states:
    state_names = [state]
  else:
    print(f"State '{state}' not found.")
    print("Available states are:\n\t" + "\n\t".join(all_states))
    state_names = []

  for state_name in state_names:
    print(f'Process {state_name}')
    state_module = importlib.import_module(f'states.{state_name}')
    state_module.main()


@task
def lint(c, warn=None):  # pylint: disable=invalid-name
  extra_opt = '--enable=all --disable=C0114,C0115,C0116 --exit-zero --reports=y' if warn else ''
  with c.cd('..'):
    c.run(f"{VENV_ACTIVATE} && pylint electoff --rcfile=.pylintrc {extra_opt}")


@task
def test(c):  # pylint: disable=unused-argument,invalid-name
  suite = unittest.TestLoader().discover('tests')
  unittest.TextTestRunner().run(suite)
