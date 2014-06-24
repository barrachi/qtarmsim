# -*- coding: utf-8 -*-

import sys
import socket
import signal

class MySocket:
    
    MSGLEN = 1024
    NL = b'\n'
    ENCODING = 'utf8'

    def __init__(self, verbose=False):
        "Creates and initializes the socket"
        self.verbose = verbose
        if self.verbose:
            print('Creating the socket')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Set conn to None
        self.conn = None
        # Set pending_lines to empty
        self.pending_lines = []
        # Asign CTRL+C signal
        signal.signal(signal.SIGINT, self.exit_signal_handler)

    def server_bind(self, port):
        """Binds the socket to a given port and starts listening. Should be used by the server application. Returns -1 if something went wrong."""
        try:
            if self.verbose:
                print('Binding to port {}'.format(port))
            self.sock.bind(('localhost', port))
        except socket.error as error:
            sys.stderr.write('Bind failed. [Errno {}] {}\n'.format(str(error.errno), error.strerror))
            sys.exit(-1)
        if self.verbose:
            print('Socket bind complete')
        self.sock.listen(1)
        if self.verbose:
            print('Socket now listening')
        return 0

    def server_accept_connection(self):
        "Waits till a connection is done. This is a blocking call. Should be used by a server application."
        if self.verbose:
            print('Waiting for a connection')
        self.conn, addr = self.sock.accept()
        if self.verbose:
            print('Connected with ' + addr[0] + ':' + str(addr[1]))
        
    def connect_to(self, port, server="localhost"):
        "Used by a client to establish a connection to the specified port."
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
        if len(self.pending_lines):
            return self.pending_lines.pop(0)
        data = self.conn.recv(self.MSGLEN)
        msg = data.decode(self.ENCODING)
        while (len(data) == self.MSGLEN and data[-1] != self.NL):
            data = self.conn.recv(self.MSGLEN)
            if len(data) == 0: # Connection closed
                #@warning: even in this case we should continue, as there could be previous read lines
                break
            msg += data.decode(self.ENCODING)
        lines = msg.strip().split('\r\n')
        if len(lines)>1:
            self.pending_lines = lines[1:]
        return lines[0]

    def receive_lines_till_eof(self):
        """
        Receives lines until a line with the EOF word is received.
        
        @return: An array with the received lines or an empty array if a timeout occurs
        """    
        lines = []
        line = self.receive_line()
        while line != 'EOF':
            lines.append(line)
            line = self.receive_line()
        if line == 'EOF': 
            return lines
        else: # timeout occurred
            return []
    
    def send_line(self, msg):
        self.conn.sendall(bytes(msg, self.ENCODING)+b'\r\n')
        
    def close_connection(self):
        if self.conn:
            self.conn.close()
            if self.verbose:
                print('Connection closed')

    def close_socket(self):
        self.sock.close()
        if self.verbose:
            print('Socket closed')

            
    def exit_signal_handler(self, signal, frame):
        self.close_socket()
