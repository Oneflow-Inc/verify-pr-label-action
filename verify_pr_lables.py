#!/usr/bin/env python3

import os
import sys
import re
from github import Github
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("--github_token", type=str, required=True)
parser.add_argument("--required_labels", action="append", nargs="+")
args = parser.parse_args()


def get_env_var(env_var_name, echo_value=False):
    """Try to get the value from a environmental variable.

    If the values is 'None', then a ValueError exception will
    be thrown.

    Args:
        env_var_name (string): The name of the environmental variable.
        echo_value (bool): Print the resulting value

    Returns:
        string: the value from the environmental variable.
    """
    value = os.environ.get(env_var_name)

    if value == None:
        raise ValueError(f"The environmental variable {env_var_name} is empty!")

    if echo_value:
        print(f"{env_var_name} = {value}")

    return value


# Get the GitHub token
token = args.github_token

# Get the list of valid labels

repo_name = get_env_var("GITHUB_REPOSITORY")
github_ref = get_env_var("GITHUB_REF")
repo = Github(token).get_repo(repo_name)

# Try to extract the pull request number from the GitHub reference.
try:
    pr_number = int(re.search("refs/pull/([0-9]+)/merge", github_ref).group(1))
    print(f"Pull request number: {pr_number}")
except AttributeError:
    raise ValueError(
        f"The Pull request number could not be extracted from the GITHUB_REF = {github_ref}"
    )

# Create a pull request object
pr = repo.get_pull(pr_number)

# Get the pull request labels
pr_labels = pr.get_labels()


is_satisfied = True


def check_labels(pr_labels, required_labels_set):
    assert len(required_labels_set) == 1, len(required_labels_set)
    splits = required_labels_set[0].split(",")

    # This is a list of valid label found in the pull request
    pr_valid_labels = []

    # Check which of the label in the pull request, are in the
    # list of valid labels
    print("checking presence:", splits)
    for label in pr_labels:
        if label.name in splits:
            pr_valid_labels.append(label.name)

    if len(pr_valid_labels):
        return True
    else:
        print(f"at least add one of these labels: `{required_labels_set}`")
        return False


required_labels_sets = args.required_labels
for required_labels_set in required_labels_sets:
    is_satisfied = check_labels(pr_labels, required_labels_set)

if is_satisfied == False:
    raise ValueError("Check fails")
