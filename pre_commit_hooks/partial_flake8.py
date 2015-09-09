#!/usr/bin/python
# coding: utf-8

import argparse
import os
import subprocess
import whatthepatch


OPTICAL_ERROR_CODES = [
    'E113',  # unexpected indentation
    'E121',  # continuation line under-indented for hanging indent
    'E123',  # closing bracket does not match indentation of opening bracket's line
    'E126',  # continuation line over-indented for hanging indent
    'E127',  # continuation line over-indented for visual indent
    'E128',  # continuation line under-indented for visual indent
    'E131',  # continuation line unaligned for hanging indent
    'E203',  # whitespace before ':'
    'E221',  # multiple spaces before operator
    'E225',  # missing whitespace around operator
    'E226',  # missing whitespace around arithmetic operator
    'E231',  # missing whitespace after ','
    'E251',  # unexpected spaces around keyword / parameter equals
    'E265',  # block comment should start with '# '
    'E302',  # expected 2 blank lines, found 1
    'E303',  # too many blank lines
    'E501',  # line too long

    'W291',  # trailing whitespace
]

REPO_ROOT = subprocess.check_output(
    'git rev-parse --show-toplevel',
    shell=True
).strip()


def _parse_flake8_errors(line):
    elements = line.split(":")
    line = elements[1]
    row = elements[2]
    error = ":".join(elements[3:])  # here can be ":" as well

    return {
        'line_number': int(line),
        'column': int(row),
        'code': error[1:5],  # the first 5 chars is error code
        'text': error[6:]  # the rest is error text
    }


def _get_flake8_errors(file_path):
    """
    Lints the file with flake8-command via popen and parses errors to dict
    """

    flake8_cfg = os.path.join(REPO_ROOT, "jobmensa", "config", "flake8.cfg")
    full_path = os.path.join(REPO_ROOT, file_path)
    params = (flake8_cfg, full_path)
    # params = (full_path)

    flake8_resp_p = subprocess.Popen(
        'flake8 --config=%s %s' % params,
        # 'flake8 %s' % params,
        shell=True,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    ).communicate()

    return [
        _parse_flake8_errors(e)
        for e in ''.join(flake8_resp_p).split("\n")
        if e
    ]


def _get_modified_lines(_file):
    # Gets the diff from GIT
    diff_patch = subprocess.check_output(
        'git diff --cached %s' % _file,
        shell=True
    )

    # Parse the patch-format and get only added or modified
    diff = [x for x in whatthepatch.parse_patch(diff_patch)]
    if not diff:
        return []

    errors = []
    for old, new, content in diff[0].changes:
        if old is None:
            errors.append(new)
            if content == '':  # if content is blank line, add next line
                errors.append(new + 1)

    return errors


def _check_for_valid_python_file(path):
    """
    Checks if the path given is a python module and if it's readable.
    """
    if not path.endswith('.py'):
        return False
    if not os.access(path, os.R_OK):
        return False
    if '/migrations/' in path:
        return False
    if '/features/' in path:
        return False
    if 'settings.py' in path:
        return False
    if path.endswith('urls.py'):
        return False
    return True


def _get_relevant_files_from_current_state(filenames):
    """
    Returns the paths to all files inside the currently created
    changeset as expected by the underlying management command.
    This hack is necessary, because the linter is called in a
    second process.
    """
    files = []
    base_path = REPO_ROOT

    for file_path in filenames:
        full_path = os.path.join(base_path, file_path)

        if _check_for_valid_python_file(full_path):
            files.append([full_path, _get_modified_lines(full_path)])

    return files


def flake8_git_hook(filenames):
    """
    This hook runs flake8 against each modified file and prevents the commit
    if there are errors found by flake8.
    """

    hook_success = 0
    hook_failed = 1

    # Check if current commit is merge commit.
    # if len(repo[node].parents()) > 1:
    #    ui.warn('We aborted because this commit is merge\n')
    #    return False

    relevant_files = _get_relevant_files_from_current_state(filenames)

    # Bail out if there are no files we wanna check.
    if not relevant_files:
        print('No files found that are worth checking\n')
        return hook_success

    total_error_count = 0
    lintered_file_count = 0

    pattern = u'\033[32m%(line_number)s\x1B[0m\t\x1B[31;40m[%(code)s]' \
              u'\x1B[0m in Column \033[34m%(column)s\x1B[0m - %(text)s'
    for file_path, modified_lines in relevant_files:
        errors = _get_flake8_errors(file_path)

        def is_significant_error(err):
            return err['code'] not in OPTICAL_ERROR_CODES or \
                err['line_number'] in modified_lines

        significant_errors = filter(is_significant_error, errors)

        if significant_errors:
            header = "***** %s ERRORS in %s *****" % (
                len(significant_errors),
                file_path
            )
            print "\n\x1B[31;40m%s\x1B[0m\n" % header
            lintered_file_count += 1

            for error in significant_errors:
                print pattern % error
                total_error_count += 1

            print '\n\x1B[31;40m%s\x1B[0m\n' % (
                ''.join('*' for i in range(len(header)))
            )

    if total_error_count > 0:
        print (
            u'Sorry, your commit is aborted, because it contains %s errors'
            u' in %s files!\n' % (total_error_count, lintered_file_count)
        )

        print u'If you are really in a rush and want to commit it anyways pl' \
              u'ease go ahead and re-commit with: \n\ngit commit --no-verify\n\n'

        return hook_failed

    return hook_success


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', nargs='*')
    args = parser.parse_args(argv)

    exit(flake8_git_hook(args.filenames))

if __name__ == '__main__':
    main()
