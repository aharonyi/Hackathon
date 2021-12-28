from server import Server
from client import Client
from threading import Thread

#Change the main!!!!!!!!!!!!!!!!!!!

def Only_client(mode = 'local'):
    cl = Client('Halva' ,mode=mode)
    t = Thread(target = cl.start)
    t.start()
    t.join()

def Client_Server(mode = 'local'):
    cl = Client('Bamba' ,mode=mode)
    t = Thread(target = cl.start)
    t.start()
    serv = Server(mode = mode)
    serv.Start()


def Only_Server(mode = 'local'):
    ser=Server(mode =mode)
    ser.Start()


if __name__=="__main__":

    Client_Server(mode = 1)
    #sleep(1)
    #Only_client(0)
    #add = scapy.get_if_addr("eth1")
    #print(type(add))

    #Only_Server(1)
