import pytest
import re
import json
import os
import logging
import jsonschema # pip install jsonschema
from jsonschema import validate

json_path = "user-agents.json"
schema_path = "schema.json"
user_agents = None              
schema = None

# This test (setup) must be run first, but once is sufficient. So it is different from setup_function that is called by Pytest before EVERY test.
# Attention, if the plugin pytest-random-order is installed, Pytest does not necessarily run the tests in the same order as in the module.
# Before v1.0.0, the plugin pytest-random-order randomises tests by default.
# To get back to the default order we have to turn off the plugin with pytest.mark.random_order(disabled=True)
def test_init_load_json_and_schema():
  is_json_loaded = False
  is_schema_loaded = False
  global user_agents
  global schema
  try:
    root_path = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    json_full_path = os.path.join(root_path, json_path)
    with open(json_full_path, 'r') as f:
      user_agents = json.load(f)
  except:
    logging.error("error loading json file %s" % json_full_path)
  else:
    is_json_loaded = True

  try:
    schema_full_path = os.path.join(root_path, schema_path)
    with open(schema_full_path, 'r') as fs:
      schema = json.load(fs)
    is_schema_loaded = True
  except:
    logging.error("error loading json schema %s" % schema_full_path)
  else:
    is_schema_loaded = True

  assert is_json_loaded and is_schema_loaded


def test_valid_json_with_schema():
  is_valid = False
  try:
    validate(instance=user_agents, schema=schema)
    is_valid = True
  except jsonschema.exceptions.ValidationError as err:
    logging.error(err)
    logging.error("json file %s is not valid according to the schema %s" % (json_path,schema_path))
  
  assert is_valid


def test_compile_regex():
  wrong_regexes = []
  for user_agent_item in user_agents:
    for regex in user_agent_item['user_agents']:
      try:
        re.compile(regex)
      except:
        wrong_regexes.append(regex)
        logging.error("regex %s could not be compiled" % regex)

  assert not bool(wrong_regexes)
