# for paths
import pathlib

# for configuration file
import toml

# for class variable type hints
from typing import ClassVar, TypedDict

# for connection
import pyodbc

# for logging
import sqlog

# get configuration file

ROLAND_ACADEMY_FILE: pathlib.Path = pathlib.Path.cwd() / "data" / "configuration" / "roland academy.toml"
ROLAND_ACADEMY: TypedDict = toml.loads(ROLAND_ACADEMY_FILE.read_text(encoding="utf-8"))

# establish dictionaries

connection_settings: TypedDict = ROLAND_ACADEMY['ConnectionSettings']


class SQLRunner:
    # get connection string and settings

    DRIVER: ClassVar[str] = connection_settings['DRIVER']
    SERVER: ClassVar[str] = connection_settings['SERVER']
    DATABASE: ClassVar[str] = connection_settings['DATABASE']
    TRUSTED_CONNECTION: ClassVar[str] = connection_settings['TRUSTED_CONNECTION']
    CONNECTION_STRING: ClassVar[str] = f"DRIVER={DRIVER}; SERVER={SERVER}; DATABASE={DATABASE}; \
    Trusted_Connection={TRUSTED_CONNECTION}"

    def __init__(self):
        # start connection

        self.connection = pyodbc.connect(self.CONNECTION_STRING)
        self.cursor = self.connection.cursor()

    def close(self):
        # close other cursors and then close the connection

        cursor = self.connection.cursor()
        cursor.close()
        self.connection.close()

    def finalize(self, commit_logger_message="...Committed...", commit_exception_message="Commit Error Occurred..."):
        try:
            sqlog.logger.info('Committing...')
            self.connection.commit()
            sqlog.logger.info(commit_logger_message)
        except pyodbc.DatabaseError:
            sqlog.logger.exception(commit_exception_message)
