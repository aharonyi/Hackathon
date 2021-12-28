import scapy.all as scapy
import socket
from threading import Thread
from threading import Lock
from time import sleep
import copy
import random

class Server:
    
    def __init__(self, mode='local'):
        self.mode = mode
        self.my_ip = self.find_my_ip()
        self.socket_tcp = None
        self.tow_players_online = False
        self.players_lck = Lock()
        self.players = []
        self.winner_lck = Lock()
        self.winner = None
        self.q = self.generate_q() 

    def generate_q(self):
        if random.randint(0,1) == 1:
            num1 = random.randint(1,8)
            num2 = random.randint(1,9-num1)
            return (str(num1)+'+'+str(num2)+'?',num1+num2)
        else:
            num1 = random.randint(2,8)
            num2 = random.randint(1,num1)
            return (str(num1)+'-'+str(num2)+'?',num1-num2)
        
    def find_my_ip(self):
        if self.mode == 'local':
            return "127.0.0.1"
        elif self.mode == 'dev':
            return scapy.get_if_addr('eth1')
        elif self.mode == 'test':
            return scapy.get_if_addr('eth2')
        raise Exception('Invalid mode- can\'t figure out an IP adress') 
        
    
    def run(self):
        print('Server started, listening on '+str(self.my_ip))
        while self.socket_tcp == None:
            tcp_port = self.start_tcp()
        broad = Thread(target = self.broadcast, args = (tcp_port,)) 
        broad.start()
        listening_to_tcp = Thread(target = self.listen_tcp)
        listening_to_tcp.start()
        
        while True:
            while not self.tow_players_online:   
                self.players_lck.acquire()
                if len(self.players) == 2:
                    self.tow_players_online = True
                self.players_lck.release()
                sleep(0.2)
            # In the game
            while self.winner ==None:
                sleep(5)
            ##recycle variables
            print('Game over, sending out offer requests...') 
            self.tow_players_online = False
            self.players = []
            self.winner = None
            self.q = self.generate_q() 

            
    def listen_tcp(self):
        try:
            self.socket_tcp.listen(2)
            while True:
                socket , addres = self.socket_tcp.accept()
                single_player = Thread(target = self.play_game, args = (socket , addres))
                single_player.start()
                sleep(0.1)
        except Exception as e:
            print('Error listening to TCP- ' + str(e))
    
    def play_game(self, c_socket, c_addres):
        try:
            name = c_socket.recv(1024).decode()
            self.players_lck.acquire()
            self.players.append(name)
            self.players_lck.release()
            
            while not self.tow_players_online :
                sleep(0.05)
            # 10 seconds after they are both in the game starts
            sleep(10)
            data_to_send = 'Welcome to Quick Maths. \n' \
                          'Player 1: '+ self.players[0] +'\n' \
                          'Player 2: '+ self.players[1] +'\n' \
                          '=== \n' \
                          'Please answer the following question as fast as you can: \n'\
                          'How much is ' + self.q[0]
            c_socket.send(data_to_send.encode())
            client_response = c_socket.recv(1024).decode()
            if self.winner_lck.acquire() and self.winner == None:
                if client_response == self.q[1]:
                    win = name
                else:
                    win = copy.deepcopy(self.players).remove(name)
                    win = win[0]
                self.winner = win
                self.winner_lck.release()
            else:
                while self.winner == None: #wait until other thread updates winner
                    sleep(0.1)
            result_data = 'Game over!\nThe correct answer was '+self.q[1]+'!\nCongratulations to the winner: '+self.winner
            c_socket.send(result_data.encode())
        except socket.timeout: 
            print('Game over!\nThe correct answer was '+self.q[1]+ '! \n No team answered in time- it\'s a draw!')
        except Exception as e:
            print('Error in game- '+ str(e))
    
    def start_tcp(self):
        try:
            new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            new_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            new_socket.bind((str(self.my_ip) , 0))
            self.socket_tcp = new_socket
            return new_socket.getsockname()[1]
        except Exception as e:
            print('Error start TCP- ' + str(e))
            
    def broadcast(self , tcp_port): 
        while True: 
            try:
                socket_broad = socket.socket(socket.AF_INET, socket.SOCK_DGRAM )
                socket_broad.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                socket_broad.settimeout(0.3)
            except Exception as e:
                print('Error at UDP creation- ' + str(e))
                socket_broad.close()
                sleep(1.5)
                continue
            print('Server started, listening on IP address ' + self.my_ip)
            
            try:
                while not self.tow_players_online:  
                    socket_broad.sendto((str(0xabcddcba) + str(0x2) + str(tcp_port)).encode(),('255.255.255.255',13117)) # ('<broadcast>',13117)
                    sleep(1)
            except Exception as e:
                print('Error in broadcast- ' + str(e))
            sleep(5)
            
            
        