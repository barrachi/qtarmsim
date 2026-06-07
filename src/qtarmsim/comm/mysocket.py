# -*- coding: utf-8 -*-

###########################################################################
#                                                                         #
#  This file is part of QtARMSim.                                         #
#                                                                         #
#  QtARMSim is free software: you can redistribute it and/or modify       #
#  it under the terms of the GNU General Public License as published by   #
#  the Free Software Foundation; either version 3 of the License, or      #
#  (at your option) any later version.                                    #
#                                                                         #
#  This program is distributed in the hope that it will be useful, but    #
#  WITHOUT ANY WARRANTY; without even the implied warranty of             #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU      #
#  General Public License for more details.                               #
#                                                                         #
###########################################################################

from __future__ import annotations

import signal
import socket
import sys
import time
from collections.abc import Generator
from typing import final

from PySide6 import QtCore


@final
class MySocket(QtCore.QObject):
    MSG_LENGTH = 1024
    NL = "\n"
    ORD_NL = 10
    ENCODING = "utf8"

    sentLine = QtCore.Signal(str)
    receivedLine = QtCore.Signal(str)

    def __init__(self, verbose: bool = False, register_sigint: bool = True) -> None:
        """
        Initializes the socket
        """
        super(MySocket, self).__init__()
        self.verbose: bool = verbose
        self.conn: socket.socket | None = None
        self.socket: socket.socket | None = None
        self.pending_lines: list[str] = []
        self.block_until_response: bool = False
        if register_sigint:
            try:
                _ = signal.signal(signal.SIGINT, self.exitSignalHandler)
            except ValueError:
                # If not in the main thread, the signal will raise a ValueError
                pass

    def serverBind(self, port: int) -> int:
        """
        Binds the socket to a given port and starts listening on that port.

        This method should be used by a server application. Returns -1 if
        something goes wrong.
        """
        if self.socket:
            self.socket.close()
            self.socket = None
        if self.verbose:
            print("Creating the socket")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            if self.verbose:
                print("Binding to port {}".format(port))
            self.socket.bind(("localhost", port))
        except socket.error as error:
            _ = sys.stderr.write(
                "Bind failed. [errno {}] {}\n".format(str(error.errno), error.strerror)
            )
            self.socket.close()
            self.socket = None
            return -1
        if self.verbose:
            print("Socket bind complete")
        # Only one listener
        self.socket.listen(1)
        if self.verbose:
            print("Socket is now listening")
        return 0

    def serverAcceptConnection(self) -> None:
        """
        Waits till a connection is done.

        This is a blocking call. Should be used by a server application.
        """
        if self.verbose:
            print("Waiting for a connection")
        assert self.socket is not None
        address: tuple[str, int]
        self.conn, address = self.socket.accept()  # pyright: ignore[reportAny]
        if self.verbose:
            print("Connected with " + address[0] + ":" + str(address[1]))

    def testPortIsFree(self, port: int) -> bool:
        """
        Tests if a port is free by binding a new socket to the given port and closing it afterwards.
        This method should only be used if a free port number has to be passed to a third application and be aware
        that there is a chance that another application grabs the port in the meantime.

        The correct way of getting a port for ourselves is using self.server_bind().

        Returns True if the port was free when the test was conducted.
        """
        err = self.serverBind(port)
        if err == 0:
            self.closeConnection()
            return True
        else:
            return False

    def connectTo(self, port: int, server: str = "localhost") -> None:
        """
        Establishes a connection to the given server at the given port.

        This method should be used by a client application.
        """
        if self.verbose:
            print("Creating the socket")
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((server, port))

    def getLines(self) -> Generator[str, None, None]:
        """
        Generator that serves each line of the received message at a time.

        Example of use:
          lines = my_socket.get_lines()
          line = lines.next()
        """
        while True:
            try:
                line = self.receiveLine()
            except ConnectionResetError:
                break
            else:
                if line != "":
                    yield line
                else:
                    break

    def _receiveLine(self) -> str:
        """
        Returns a line from the line received queue or gets a new one.

        @return: a line.
        """
        if len(self.pending_lines):
            line = self.pending_lines[0]
            self.pending_lines = self.pending_lines[
                1:
            ]  # will be [] if there are no more pending lines
            if self.verbose:
                print("Received line: {}".format(line))
            self.receivedLine.emit(line)
            return line
        assert self.conn is not None
        chunk = self.conn.recv(self.MSG_LENGTH)
        if self.verbose:
            print("Received chunk of size: {}".format(len(chunk)))
            print("Contents:\n #{}#".format(chunk))
        data = chunk
        # Grab more chunks while the other end does not disconnect and the received chunk does not end with \n
        while len(chunk) != 0 and chunk[-1] != self.ORD_NL:
            chunk = self.conn.recv(self.MSG_LENGTH)
            if self.verbose:
                print("Received chunk of size: {}".format(len(chunk)))
                print("Contents: #{}#".format(chunk))
            data += chunk
        try:
            msg = data.decode(self.ENCODING)
        except UnicodeDecodeError:
            msg = data.decode("latin1")
        lines = [
            line.strip()
            for line in msg.strip().replace("\r\n", "\n").split("\n")
            if line.strip() != ""
        ]
        if len(lines):
            line = lines[0]
            self.pending_lines = lines[1:]  # will be [] if there are no more lines
            if self.verbose:
                print("Received line: {}".format(line))
            self.receivedLine.emit(line)
            return line
        else:
            return ""

    def receiveLine(self) -> str:
        """
        Returns a line from self._receive_line() and clears the block_until_response flag.

        @return: a line.
        """
        line = self._receiveLine()
        self.block_until_response = False
        return line

    def receiveLinesTillEof(self) -> Generator[str, None, None]:
        """
        Receives lines until a line with the EOF word is received.

        @return: An array with the received lines or an empty array if a timeout occurs.
        """
        lines: list[str] = []  # For giving some information if a timeout occurs
        line = ""
        while line != "EOF":
            try:
                line = self._receiveLine()
            except socket.timeout:
                print("A time out error has occurred")
                print("\n".join(lines))
                raise
            lines.append(line)
            if line != "EOF":
                yield line
        self.block_until_response = False

    def sendLine(self, msg: str) -> None:
        """
        Sends a line through the open connection.
        """
        # Avoid sending new commands to ARMSim until the block_until_response flag is cleared
        deadline = time.monotonic() + 10.0
        while self.block_until_response:
            if time.monotonic() > deadline:
                self.block_until_response = False
                break
            time.sleep(0.1)
        if self.verbose:
            print("Sending line: {}".format(msg))
        self.block_until_response = True
        assert self.conn is not None
        self.conn.sendall(bytes(msg, self.ENCODING) + b"\r\n")
        self.sentLine.emit(msg)

    def closeConnection(self) -> None:
        """
        Closes the current connection and the listening socket if open.
        """
        if self.conn:
            self.conn.close()
            self.conn = None
            if self.verbose:
                print("Connection closed")
        if self.socket:
            self.socket.close()
            self.socket = None

    def exitSignalHandler(self, _sig: int, _frame: object) -> None:
        """
        Handler used to close the socket when an exit signal is received. See __init__().
        """
        self.closeConnection()
        sys.exit(0)

    def setConnTimeout(self, value: float) -> None:
        """
        Sets the timeout for the connection if it is established. This function
        configures the timeout duration for the current connection to ensure
        that operations do not block indefinitely.

        :param value: The timeout duration in seconds to set for the connection.
        :type value: float
        :return: None
        """
        if self.conn:
            self.conn.settimeout(value)