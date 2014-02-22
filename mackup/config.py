"""
Package used to manage the .mackup.cfg config file
"""

import os
import os.path

from constants import (MACKUP_BACKUP_PATH,
                       MACKUP_CONFIG_FILE,
                       ENGINE_DROPBOX,
                       ENGINE_GDRIVE,
                       ENGINE_FS)

from utils import (get_dropbox_folder_location,
                   get_google_drive_folder_location)

try:
    import configparser
except ImportError:
    import ConfigParser as configparser


class Config(object):

    def __init__(self, filename=None):
        """
        Args:
            filename (unicode): Optional filename of the config file. If empty,
                                defaults to MACKUP_CONFIG_FILE
        """
        assert isinstance(filename, str) or filename is None

        # Initialize the parser
        self._parser = self._setup_parser(filename)

        # Do we have an old config file ?
        self._warn_on_old_config()

        # Get the storage engine
        self._engine = self._parse_engine()

        # Get the path where the Mackup folder is
        self._path = self._parse_path()

        # Get the directory replacing 'Mackup', if any
        self._directory = self._parse_directory()

    @property
    def engine(self):
        """
        The engine used by the storage.
        ENGINE_DROPBOX, ENGINE_GDRIVE or ENGINE_FS.

        Returns:
            unicode
        """
        return unicode(self._engine)

    @property
    def path(self):
        """
        The path to the directory where Mackup is gonna create and store his
        directory.

        Returns:
            unicode
        """
        return unicode(self._path)

    @property
    def directory(self):
        """
        The name of the Mackup directory, named Mackup by default.

        Returns:
            unicode
        """
        return unicode(self._directory)

    @property
    def fullpath(self):
        """
        The full path to the directory when Mackup is storing the configuration
        files.

        Returns:
            unicode
        """
        return unicode(os.path.join(self.path, self.directory))

    def _setup_parser(self, filename=None):
        """
        Args:
            filename (unicode) or None

        Returns:
            SafeConfigParser
        """
        assert isinstance(filename, str) or filename is None

        # If we are not overriding the config filename
        if not filename:
            filename = MACKUP_CONFIG_FILE

        parser = configparser.SafeConfigParser(allow_no_value=True)
        parser.read(os.path.join(os.path.join(os.environ['HOME'], filename)))

        return parser

    def _warn_on_old_config(self):
        # Is an old setion is in the config file ?
        old_sections = ['Allowed Applications', 'Ignored Applications']
        for old_section in old_sections:
            if self._parser.has_section(old_section):
                utils.error("Old config file detected. Aborting.\n"
                            "\n"
                            "An old section (e.g. [Allowed Applications]"
                            " or [Ignored Applications] has been detected"
                            " in your {} file.\n"
                            "I'd rather do nothing than do something you"
                            " do not want me to do.\n"
                            "\n"
                            "Please read the up to date documentation on"
                            " <https://github.com/lra/mackup> and migrate"
                            " your configuration file."
                            .format(path_to_cfg))

    def _parse_engine(self):
        """
        Returns:
            unicode
        """
        if self._parser.has_option('storage', 'engine'):
            engine = unicode(self._parser.get('storage', 'engine'))
        else:
            engine = ENGINE_DROPBOX

        assert isinstance(engine, unicode)

        if engine not in [ENGINE_DROPBOX, ENGINE_GDRIVE, ENGINE_FS]:
            raise ConfigError('Unknown storage engine: {}'.format(engine))

        return unicode(engine)

    def _parse_path(self):
        """
        Returns:
            unicode
        """
        if self.engine == ENGINE_DROPBOX:
            path = unicode(get_dropbox_folder_location())
        elif self.engine == ENGINE_GDRIVE:
            path = get_google_drive_folder_location()
        elif self.engine == ENGINE_FS:
            if self._parser.has_option('storage', 'path'):
                cfg_path = unicode(self._parser.get('storage', 'path'))
                path = os.path.join(os.environ['HOME'], cfg_path)
            else:
                raise ConfigError("The required 'path' can't be found while the"
                                  " 'file_system' engine is used.")

        return unicode(path)

    def _parse_directory(self):
        """
        Returns:
            unicode
        """
        if self._parser.has_option('storage', 'directory'):
            directory = self._parser.get('storage', 'directory')
        else:
            directory = MACKUP_BACKUP_PATH

        return unicode(directory)


class ConfigError(Exception):
    pass
