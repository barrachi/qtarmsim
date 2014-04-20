# -*- coding: utf-8 -*-

import sys
import socket
import signal

class MySocket:
    
    MSGLEN = 1024
    NL = b'\n'
    ENCODING = 'ascii'

    def __init__(self):
        "Creates and initializes the socket"
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
            print('Binding to port {}'.format(port))
            self.sock.bind(('localhost', port))
        except socket.error as error:
            sys.stderr.write('Bind failed. [Errno {}] {}\n'.format(str(error.errno), error.strerror))
            sys.exit(-1)
        print('Socket bind complete')
        self.sock.listen(1)
        print('Socket now listening')
        return 0

    def server_accept_connection(self):
        "Waits till a connection is done. This is a blocking call. Should be used by a server application."
        print('Waiting for a connection')
        self.conn, addr = self.sock.accept()
        print('Connected with ' + addr[0] + ':' + str(addr[1]))
        
    def connect_to(self, port):
        "Used by a client to establish a connection to the specified port."
        self.sock.connect(("localhost", port))
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
    
    def send_line(self, msg):
        self.conn.sendall(bytes(msg, self.ENCODING)+b'\r\n')
        
    def close_connection(self):
        if self.conn:
            self.conn.close()
            print('Connection closed')

    def close_socket(self):
        self.sock.close()
        print('Socket closed')

            
    def exit_signal_handler(self, signal, frame):
        self.close_socket()
