#!/usr/bin/python3

# rdfunit_wrapper.py
# Date:  21/09/2020
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" This module implements wrappers around a external RDF validation tools. """

import abc
import logging
from subprocess import Popen, PIPE


class SubprocessFailure(Exception):
    """
        An exception for SKOSHistoryRunner.
    """


class AbstractValidatorWrapper(abc.ABC):
    __COMMAND__: str

    @abc.abstractmethod
    def __init__(self, command):
        self.__logger = logging.getLogger(__name__)
        self.__COMMAND__ = command

    @abc.abstractmethod
    def run(self, *args):
        pass

    def execute_subprocess(self, *args):
        self.__logger.info('Subprocess starting: ' + self.__COMMAND__)
        
        process = Popen(
            [self.__COMMAND__, *args],
            stdout=PIPE)
        output, _ = process.communicate()

        if process.returncode != 0:
            self.__logger.fatal('Subprocess failed: ' + self.__COMMAND__)
            self.__logger.fatal(f'Subprocess: {output.decode()}')
            raise SubprocessFailure(output)

        self.__logger.info('Subprocess finished successfully: ' + self.__COMMAND__ + " with arguments: " + str(args))
        return output.decode()


class RDFUnitWrapper(AbstractValidatorWrapper):

    def __init__(self, command):
        super().__init__(command)

    def run(self, *args):
        self.execute_subprocess(args)
