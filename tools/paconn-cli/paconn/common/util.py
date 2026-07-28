# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------
"""
Utility methods.
"""
import sys
import os
import io
import json

import requests

from knack.util import CLIError
from knack.prompting import prompt_y_n


def get_config_dir():
    """
    Returns the user config directory.
    """
    from paconn import __CLI_NAME__
    return os.path.expanduser(os.path.join('~', '.{}'.format(__CLI_NAME__)))


def display(txt):
    """
    Displayed the text to stderr stream.
    """
    print(txt, file=sys.stderr)


def format_json(content, sort_keys=False):
    """
    Format a given dictionary to a json formatted string.
    """
    json_string = json.dumps(
        content,
        sort_keys=sort_keys,
        indent=2,
        separators=(',', ': '))
    return json_string


def write_file(filename, content, mode='w'):
    """
    Write the content to the given file.
    """
    with open(filename, mode=mode) as file:
        file.write(content)


def load_json_file(filename):
    """
    Load a json file, ignoring the byte order mark when present.
    """
    with io.open(filename, 'r', encoding='utf-8-sig') as file:
        return json.load(file)


def download_content(url):
    """
    Returns the content of a given url.
    """
    response = requests.get(url, allow_redirects=True)
    return response.content


def ensure_file_exists(file, file_type):
    """
    Check if the given file exists.
    """

    if not file:
        raise CLIError('{} must be specified.'.format(file_type))
    if not os.path.exists(file):
        raise CLIError('File does not exist: {}'.format(file))


def ensure_overwrite(filename):
    overwrite = True
    if os.path.exists(filename):
        msg = '{} file exists. Do you want to overwrite?'.format(filename)
        overwrite = prompt_y_n(msg)

    return overwrite


def write_with_prompt(filename, mode, content, overwrite):
    if not overwrite:
        overwrite = ensure_overwrite(filename)

    if overwrite:
        write_file(filename=filename, content=content, mode=mode)
