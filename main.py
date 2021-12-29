from server import Server
from client import Client
from threading import Thread

def main():
    mode = 'local'

    server = Server(mode =mode)
    server_t = Thread(target = server.run)
    
    client1 = Client('Rick', mode=mode)
    client1_t = Thread(target = client1.run)

    client2 = Client('Morty', mode=mode)
    client2_t = Thread(target = client2.run)

    client2_t.start()
    client1_t.start()
    server_t.start()


if __name__=="__main__":

    main()
    

