import pytest
import re
import json
import os
import logging

root_path = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
json_path = os.path.join(root_path, "user-agents.json")
with open(json_path, 'r') as f:
  user_agents = json.load(f)

def test_compile_regex():
  wrong_regexes = []
  for user_agent_item in user_agents:
    for regex in user_agent_item['user_agents']:
      try:
        re.compile(regex)
      except:
        wrong_regexes.append(regex)
        logging.error("regex %s could not be compiled" % regex)

  assert not wrong_regexes

def test_unique_regex():
  regexes = set()
  duplicates = []
  for user_agent_item in user_agents:
    for regex in user_agent_item['user_agents']:
      if (regex not in regexes):
        regexes.add(regex)
      else:
        duplicates.append(regex)
        logging.error("regex %s is not unique" % regex)

  assert not duplicates

def test_unique_correct_matching_regex_for_examples():
  examples = []
  regexes = []

  no_matching_issues = []
  unexpected_matching_issues = []
  duplicate_issues = []

  # get all examples and regexes
  for idx, user_agent_item in enumerate(user_agents):
    for regex in user_agent_item['user_agents']:
      pattern = re.compile(regex)
      regexes.append({'id':idx, 'pattern':pattern})
    for example in user_agent_item.get('examples',[]):
      examples.append({'user_agent_string':example, 'expected_id':idx})
  
  # test every example whith every regex
  for example in examples:
    user_agent_string = example['user_agent_string']
    correct_matching_regex = None

    for regex in regexes:
      if regex['pattern'].search(user_agent_string): # match() checks for a match only at the beginning https://docs.python.org/3/library/re.html#search-vs-match
        if regex['id'] != example['expected_id']:
          unexpected_matching_issues.append("unexpected matching regex for \"%s\" with \"%s\"" % (user_agent_string, regex['pattern'].pattern))
        else:
          if correct_matching_regex: # already matched
            duplicate_issues.append("duplicate matching regex for \"%s\" with \"%s\"" % (correct_matching_regex['pattern'].pattern, regex['pattern'].pattern))
          else:
            correct_matching_regex = regex
    
    if correct_matching_regex is None:
      no_matching_issues.append("no matching regex for \"%s\"" % user_agent_string)

  # print errors
  for issue in no_matching_issues + unexpected_matching_issues + duplicate_issues:
    logging.error(issue)

  logging.error("\nno matching issue(s):\t\t%s\nunexpected matching issue(s):\t%s\nduplicate issue(s):\t\t%s" % (len(no_matching_issues), len(unexpected_matching_issues), len(duplicate_issues)))
  
  assert not no_matching_issues and not unexpected_matching_issues and not duplicate_issues
