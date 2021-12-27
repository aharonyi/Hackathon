import socket
from time import sleep

class Client:
    
    def __init__(self, name, mode='local'):
        self.name = name #The name of the team
        self.socket_udp = None
        self.socket_tcp = None
        self.mode = mode
        self.cookie = str(0xabcddcba)
        
    def get_udp_socket(self):
        try:
            new_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM )
            
            # Avoid bind() exception: OSError: [Errno 48] Address already in use
            new_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Enable the socket for issuing messages to a broadcast address.
            new_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            new_socket.bind(("" , 13117))
        
        except Exception as e:
            print('Error in UDP- '+str(e))
            new_socket.close()
            return None

        
        return new_socket

    def process_msg(self, data):
            try:
                if data[:10] != self.cookie:
                    print('Message received with wrong cookie')
                    return None
                if data[10] != '2':
                    print('Can only support offer type messages')
                    return None
            except Exception as e:
                print('exception: the message can\'t be processed - '+str(e))
                return None

            return int(data[11:])
    
    def get_tcp_info(self):
        while True:
            server_port = None
            try:
                data, server_add = self.socket_udp.recvfrom(2048)
                server_port = self.process_msg(data.decode())

            except Exception as e:
                print('Error in TCP- ' +str(e))
            if server_port != None:
                break
            sleep(1)

        return server_add[0], server_port
        
    def connect(self, server_add, server_port):
        if self.mode == 'local':  
            server_add = "127.0.0.1" #localhost
        try:
            new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            new_socket.settimeout(20)
            new_socket.connect((server_add, server_port))
            self.socket_tcp = new_socket
        except Exception as e:
            print("can/'t connect to server in TCP- " + str(e))
            new_socket.close()
            self.socket_tcp = None
            
    def start_playing(self):
        try:
            self.socket_tcp.send((str(self.name) + ' \n').encode())
            question = self.tcp_socket.recv(1024).decode()
            answer = input(question)
            self.socket_tcp.send(answer.encode())
            game_result = self.socket_tcp.recv(1024)
            print(game_result.decode())
            self.socket_tcp.close()

        
        except Exception as e:
            print('error in game - ' + str(e))
            self.socket_tcp.close()

        self.socket_tcp = None

        return 
            
    def run(self):
        while True:
            # Start UDP 
            print('Client started, listening for offer requests...')
            while self.socket_udp == None:    
                self.socket_udp = self.get_udp_socket()
                sleep(0.3)     
            # Start TCP
            server_add ,server_port = self.get_tcp_info()
            print('Received offer from '+str(server_add)+', attempting to connect...')
    
            self.connect(server_add ,server_port)
    
            if not self.socket_tcp is None:
                self.start_playing()
                print('Server disconnected, listening for offer requests...')
            sleep(0.5)
            