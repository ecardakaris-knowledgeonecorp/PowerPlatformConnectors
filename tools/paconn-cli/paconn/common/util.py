# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------
"""
Utility methods.
"""
import io
import sys
import os
import json

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


def ensure_file_exists(file, file_type):
    """
    Check if the given file exists.
    """

    if not file:
        raise CLIError('{} must be specified.'.format(file_type))
    if not os.path.exists(file):
        raise CLIError('File does not exist: {}'.format(file))


def load_json_file(filename, file_type, encoding='utf-8-sig'):
    """
    Load a JSON document from a file and fail with an actionable error.
    """
    try:
        with io.open(filename, 'r', encoding=encoding) as file:
            return json.load(file)
    except ValueError as exception:
        raise CLIError('{file_type} file {filename} is not a valid JSON document. (Inner Error: {error})'.format(
            file_type=file_type,
            filename=filename,
            error=exception)) from exception
    except OSError as exception:
        raise CLIError('Couldn\'t read the {file_type} file {filename}. (Inner Error: {error})'.format(
            file_type=file_type,
            filename=filename,
            error=exception)) from exception


def write_file(filename, mode, content):
    """
    Write content to a file and fail with an actionable error.
    """
    try:
        with open(filename, mode=mode) as file:
            file.write(content)
    except OSError as exception:
        raise CLIError('Couldn\'t write the file {filename}. (Inner Error: {error})'.format(
            filename=filename,
            error=exception)) from exception


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
        write_file(filename=filename, mode=mode, content=content)
    else:
        display('{} is not overwritten.'.format(filename))
