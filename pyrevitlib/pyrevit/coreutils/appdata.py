"""Utility functions for creating data files within pyRevit environment.

Most times, scripts need to save some data to shared between different scripts
that work on a similar topic or between script executions. This module provides
the necessary and consistent mechanism for creating and maintaining such files.

Example:
    >>> from pyrevit.coreutils import appdata
    >>> appdata.list_data_files()
"""

import os
import os.path as op
import re

from pyrevit import PYREVIT_APP_DIR, PYREVIT_VERSION_APP_DIR, EXEC_PARAMS
from pyrevit import PYREVIT_FILE_PREFIX_UNIVERSAL,\
                    PYREVIT_FILE_PREFIX, PYREVIT_FILE_PREFIX_STAMPED
from pyrevit.coreutils import make_canonical_name
from pyrevit.coreutils.logger import get_logger


logger = get_logger(__name__)


TEMP_FILE_EXT = 'tmp'


def _remove_app_file(file_path):
    try:
        os.remove(file_path)
    except Exception as osremove_err:
        logger.error('Error file cleanup on: {} | {}'
                     .format(file_path, osremove_err))


def _list_app_files(prefix, file_ext, universal=False):
    requested_files = []

    if universal:
        appdata_folder = PYREVIT_APP_DIR
    else:
        appdata_folder = PYREVIT_VERSION_APP_DIR

    for appdata_file in os.listdir(appdata_folder):
        if appdata_file.startswith(prefix) and appdata_file.endswith(file_ext):
            requested_files.append(op.join(appdata_folder, appdata_file))

    return requested_files


def _get_app_file(file_id, file_ext,
                  filename_only=False, stamped=False, universal=False):
    appdata_folder = PYREVIT_VERSION_APP_DIR
    file_prefix = PYREVIT_FILE_PREFIX

    if stamped:
        file_prefix = PYREVIT_FILE_PREFIX_STAMPED
    elif universal:
        appdata_folder = PYREVIT_APP_DIR
        file_prefix = PYREVIT_FILE_PREFIX_UNIVERSAL

    full_filename = '{}_{}.{}'.format(file_prefix, file_id, file_ext)

    if filename_only:
        return full_filename
    else:
        return op.join(appdata_folder, full_filename)


def get_universal_data_file(file_id, file_ext, name_only=False):
    """Get path to file that is shared between all host versions.

    These data files are not cleaned up at Revit restart.
    e.g pyrevit_eirannejad_file_id.file_ext

    Args:
        file_id (str): Unique identifier for the file
        file_ext (str): File extension
        name_only (bool): If true, function returns file name only

    Returns:
        str: File name or full file path (depending on name_only)
    """
    return _get_app_file(file_id, file_ext,
                         filename_only=name_only, universal=True)


def get_data_file(file_id, file_ext, name_only=False):
    """Get path to file that will not be cleaned up at Revit load.

    e.g pyrevit_2016_eirannejad_file_id.file_ext

    Args:
        file_id (str): Unique identifier for the file
        file_ext (str): File extension
        name_only (bool): If true, function returns file name only

    Returns:
        str: File name or full file path (depending on name_only)
    """
    return _get_app_file(file_id, file_ext, filename_only=name_only)


def get_instance_data_file(file_id, file_ext=TEMP_FILE_EXT, name_only=False):
    """Get path to file that should be used by current instance only.

    These data files will be cleaned up at Revit restart.
    e.g pyrevit_2016_eirannejad_2353_file_id.file_ext

    Args:
        file_id (str): Unique identifier for the file
        file_ext (str): File extension
        name_only (bool): If true, function returns file name only

    Returns:
        str: File name or full file path (depending on name_only)
    """
    return _get_app_file(file_id, file_ext,
                         filename_only=name_only, stamped=True)


def is_pyrevit_data_file(file_name):
    """Check if given file is a pyRevit data file.

    Args:
        file_name (str): file name

    Returns:
        bool: True if file is a pyRevit data file
    """
    return PYREVIT_FILE_PREFIX in file_name


def is_file_available(file_name, file_ext, universal=False):
    """Check if given file is available within appdata directory.

    Args:
        file_name (str): file name
        file_ext (str): file extension
        universal (bool): Check against universal data files

    Returns:
        str: file path if file is available
    """
    if universal:
        full_filename = op.join(PYREVIT_APP_DIR,
                                make_canonical_name(file_name, file_ext))
    else:
        full_filename = op.join(PYREVIT_VERSION_APP_DIR,
                                make_canonical_name(file_name, file_ext))
    if op.exists(full_filename):
        return full_filename
    else:
        return False


def is_data_file_available(file_id, file_ext):
    """Check if given file is available within appdata directory.

    Args:
        file_id (str): data file id
        file_ext (str): file extension

    Returns:
        str: file path if file is available
    """
    full_filename = _get_app_file(file_id, file_ext)
    if op.exists(full_filename):
        return full_filename
    else:
        return False


def list_data_files(file_ext, universal=False):
    """List all data files with given extension.

    Args:
        file_ext (str): file extension
        universal (bool): Check against universal data files

    Returns:
        :obj:`list`: list of files
    """
    return _list_app_files(PYREVIT_FILE_PREFIX, file_ext, universal=universal)


def list_session_data_files(file_ext):
    """List all data files associated with current session.

    Args:
        file_ext (str): data files with this extension will be listed only.

    Returns:
        :obj:`list`: list of data files

    """
    return _list_app_files(PYREVIT_FILE_PREFIX_STAMPED, file_ext)


def garbage_data_file(file_path):
    """Mark and remove the given appdata file.

    Current implementation removes the file immediately.

    Args:
        file_path (str): path to the target file
    """
    _remove_app_file(file_path)


def cleanup_appdata_folder():
    """Cleanup appdata folder of all temporary appdata files."""
    if EXEC_PARAMS.first_load:
        finder = re.compile(r'(.+)_(.+)_(.+)_(\d+).+')
        for appdata_file in os.listdir(PYREVIT_VERSION_APP_DIR):
            file_name_pieces = finder.findall(appdata_file)
            if file_name_pieces \
                    and len(file_name_pieces[0]) == 4 \
                    and int(file_name_pieces[0][3]) > 0 \
                    and appdata_file.endswith(TEMP_FILE_EXT):
                _remove_app_file(op.join(PYREVIT_VERSION_APP_DIR,
                                         appdata_file))
