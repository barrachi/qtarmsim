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

import signal
import socket
import sys


class MySocket:

    MSGLEN = 1024
    NL = '\n'
    ORD_NL = 10
    ENCODING = 'utf8'

    def __init__(self, verbose=False):
        """
        Initializes the socket
        """
        self.verbose = verbose
        self.conn = None
        self.pending_lines = []
        try:
            signal.signal(signal.SIGINT, self.exit_signal_handler)
        except ValueError:
            # If not in main thread signal will raise a ValueError
            pass

    def server_bind(self, port):
        """
        Binds the socket to a given port and starts listening on that port.

        This method should be used by a server application. Returns -1 if
        something goes wrong.
        """
        if self.verbose:
            print('Creating the socket')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            if self.verbose:
                print('Binding to port {}'.format(port))
            self.sock.bind(('localhost', port))
        except socket.error as error:
            sys.stderr.write('Bind failed. [Errno {}] {}\n'.format(str(error.errno), error.strerror))
            return -1
        if self.verbose:
            print('Socket bind complete')
        # Only one listener
        self.sock.listen(1)
        if self.verbose:
            print('Socket now listening')
        return 0

    def server_accept_connection(self):
        """
        Waits till a connection is done.

        This is a blocking call. Should be used by a server application.
        """
        if self.verbose:
            print('Waiting for a connection')
        self.conn, addr = self.sock.accept()
        if self.verbose:
            print('Connected with ' + addr[0] + ':' + str(addr[1]))

    def test_port_is_free(self, port):
        """
        Tests if a port is free by binding a new socket to the given port and closing it afterwards.
        This method should only be used if a free port number has to passed to a third application, and be aware that
        there is a chance that another application grabs the port in the meantime.

        The correct way of getting a port for ourselves is using self.server_bind().

        Returns True if the port was free when the test was conducted.
        """
        err = self.server_bind(port)
        if err==0:
            self.close_socket()
            return True
        else:
            return False

    def connect_to(self, port, server="localhost"):
        """
        Establishes a connection to the given server at the given port.

        This method should be used by a client application.
        """
        if self.verbose:
            print('Creating the socket')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((server, port))
        self.conn = self.sock

    def get_lines(self):
        """
        Generator that serves each line of the received message at a time.

        Example of use:
          lines = mysocket.get_lines()
          line = lines.next()
        """
        while True:
            try:
                line = self.receive_line()
            except ConnectionResetError:
                break
            if line != '':
                yield line
            else:
                break


    def receive_line(self):
        """
        Returns a line from the line received queue or gets a new one.

        @return: a line.
        """
        if len(self.pending_lines):
            line = self.pending_lines.pop(0)
            if self.verbose:
                print("Received line: {}".format(line))
            return line
        chunk = self.conn.recv(self.MSGLEN)
        if self.verbose:
            print("Received chunk of size: {}".format(len(chunk)))
            print("Contents:\n #{}#".format(chunk))
        data = chunk
        # Grab more chunks while the other end does not disconnect AND the received chunk does not end with \n
        while len(chunk)!=0 and chunk[-1] != self.ORD_NL:
            chunk = self.conn.recv(self.MSGLEN)
            if self.verbose:
                print("Received chunk of size: {}".format(len(chunk)))
                print("Contents: #{}#".format(chunk))
            data += chunk
        try:
            msg = data.decode(self.ENCODING)
        except UnicodeDecodeError:
            msg = data.decode('latin1')
        lines = [l.strip() for l in msg.strip().replace('\r\n', '\n').split('\n') if l.strip() != ""]
        if len(lines)>1:
            self.pending_lines = lines[1:]
        if len(lines):
            line = lines[0]
            if self.verbose:
                print("Received line: {}".format(line))
            return line
        else:
            return ""

    def receive_lines_till_eof(self):
        """
        Receives lines until a line with the EOF word is received.

        @return: An array with the received lines or an empty array if a timeout occurs.
        """
        lines = []
        line = ''
        while line != 'EOF':
            try:
                line = self.receive_line()
            except socket.timeout:
                print("A time out error has occurred")
                print("\n".join(lines))
                raise
            lines.append(line) # For debugging purposes only
            if line != 'EOF':
                yield line

    def send_line(self, msg):
        """
        Sends a line through the open connection.
        """
        self.conn.sendall(bytes(msg, self.ENCODING)+b'\r\n')

    def close_connection(self):
        """
        Closes the current connection.
        """
        if self.conn:
            self.conn.close()
            if self.verbose:
                print('Connection closed')

    def close_socket(self):
        """
        Closes the current socket.
        """
        self.sock.close()
        if self.verbose:
            print('Socket closed')


    def exit_signal_handler(self, signal, frame):
        """
        Handler used to closes the socket when an exit signal is received. See __init__().
        """
        self.close_socket()
