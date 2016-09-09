#!/usr/bin/env python
"""
For Checking Python Imported Module
"""

import os
import sys
import fnmatch
import itertools


# File patterns to include in the non-WPT tidy check.
FILE_PATTERNS_TO_CHECK = ["*.py"]

# File patterns that are ignored for all tidy and lint checks.
FILE_PATTERNS_TO_IGNORE = ["*.#*", "*.pyc", "__init__.py"]

# Files that are ignored for all tidy and lint checks.
IGNORED_FILES = [
    os.path.join(".", "stat.json"),
    os.path.join(".", "client_secrets.json"),
    os.path.join(".", "result.json"),
    # Hidden files
    os.path.join(".", "."),
]

# Directories that are ignored for the non-WPT tidy check.
IGNORED_DIRS = [
    # Upstream
    os.path.join(".", "build"),
    os.path.join(".", "dist"),
    os.path.join(".", "flows"),
    os.path.join(".", "output"),
    os.path.join(".", "thirdParty"),
    os.path.join(".", "resource"),
    os.path.join(".", "python", "_virtualenv"),
    os.path.join(".", "python", "tidy"),
    # Hidden directories
    os.path.join(".", "."),
]


class ImportModuleChecker(object):
    def __init__(self):
        self.current_file_dir = os.path.dirname(os.path.realpath(__file__))

    @staticmethod
    def is_iter_empty(iterator):
        try:
            obj = iterator.next()
            return True, itertools.chain((obj,), iterator)
        except StopIteration:
            return False, iterator

    @staticmethod
    def progress_wrapper(iterator):
        list_of_stuff = list(iterator)
        total_files, progress = len(list_of_stuff), 0
        for idx, thing in enumerate(list_of_stuff):
            progress = int(float(idx + 1) / total_files * 100)
            sys.stdout.write('\r  Progress: %s%% (%d/%d)' % (progress, idx + 1, total_files))
            sys.stdout.flush()
            yield thing

    @staticmethod
    def filter_file(file_name):
        if any(file_name.startswith(ignored_file) for ignored_file in IGNORED_FILES):
            return False
        base_name = os.path.basename(file_name)
        if any(fnmatch.fnmatch(base_name, pattern) for pattern in FILE_PATTERNS_TO_IGNORE):
            return False
        return True

    @staticmethod
    def filter_files(start_dir, progress):
        file_iter = ImportModuleChecker.get_file_list(start_dir, IGNORED_DIRS)
        (has_element, file_iter) = ImportModuleChecker.is_iter_empty(file_iter)
        if not has_element:
            raise StopIteration
        if progress:
            file_iter = ImportModuleChecker.progress_wrapper(file_iter)
        for file_name in file_iter:
            base_name = os.path.basename(file_name)
            if not any(fnmatch.fnmatch(base_name, pattern) for pattern in FILE_PATTERNS_TO_CHECK):
                continue
            if not ImportModuleChecker.filter_file(file_name):
                continue
            yield file_name

    @staticmethod
    def get_file_list(directory, exclude_dirs=[]):
        if exclude_dirs:
            for root, dirs, files in os.walk(directory, topdown=True):
                # modify 'dirs' in-place so that we don't do unwanted traversals in excluded directories
                dirs[:] = [d for d in dirs if not any(os.path.join(root, d).startswith(name) for name in exclude_dirs)]
                for rel_path in files:
                    yield os.path.join(root, rel_path)
        else:
            for root, _, files in os.walk(directory):
                for f in files:
                    yield os.path.join(root, f)

    def run(self):
        files_to_check = ImportModuleChecker.filter_files('./lib', progress=True)

        (has_element, files_to_check) = ImportModuleChecker.is_iter_empty(files_to_check)
        if not has_element:
            raise StopIteration
        print('[INFO] Checking files for imported modules ...')

        ret_set = set()
        for filename in files_to_check:
            if not os.path.exists(filename):
                continue
            with open(filename, "r") as f:
                contents = f.read()
                ret_set.update(line for line in contents.splitlines(True) if line.startswith('import ') or line.startswith('from '))

        import_set = set()
        for import_string in ret_set:
            if 'NOQA' in import_string:
                continue
            elif import_string.startswith('import '):
                import_set.add(import_string.strip().replace('import ', ''))
            elif import_string.startswith('from '):
                import_set.add(import_string.strip().replace('from ', '').replace(' import ', '.'))
        return import_set


def main():
    try:
        ret = ImportModuleChecker().run()
        print('')
        print(ret)
        print('[INFO] Running python CV2 module passed.')
    except Exception as e:
        print('[Error] Running python CV2 module failed.')
        print(e)
        exit(1)


if __name__ == '__main__':
    main()
