#Le serveur permet de mémoriser la liste des clients disponibles pour chatter. 
#Il retient pour chaque client son pseudo et son adresse IP.
#Au démarrage, Le client va se présenter au serveur, ce qui fait qu’il sera disponible pour chatter.
 #Il peut interroger le serveur pour obtenir la liste des clients disponibles.
#Ayant l’adresse IP d’une autre machine, une machine peut lancer un chat avec une autre en mode peer-to-peer, 
#tout cela indépendamment du serveur.

# tcp entre serrveur et machine 
# udp entre machine 
# et donc nécessairement 2 sockets différents
# join [ip] pour démarrer le chat 
# ecoute par 0.0.0.0. veut dire que l'ordi écoute par toutes les adresses 
import pickle
import socket
import struct
import sys
import threading


Port = 6000 

class Chat:

    def __init__(self, host="0.0.0.0", port=5000):

        s = socket.socket(type=socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.bind((host, port))
        self.__s = s

        print('Écoute sur {}:{}'.format(host, port))

        

    def run(self):
        handlers = {
            '/exit': self._exit,
            '/quit': self._quit,
            '/join': self._join,
            '/send': self._send
        }

        self.__running = True
        self.__address = None
        threading.Thread(target=self._receive).start()
        while self.__running:
            line = sys.stdin.readline().rstrip() + ' '
            # Extract the command and the param
            command = line[:line.index(' ')]
            param = line[line.index(' ')+1:].rstrip()

            # Call the command handler

            if command in handlers:
                try:
                    handlers[command]() if param == '' else handlers[command](param)
                except:
                    print("Erreur lors de l'exécution de la commande.")

            else:
                print('Command inconnue:', command)

    

    def _exit(self):
        self.__running = False
        self.__address = None
        self.__s.close()

    

    def _quit(self):
        self.__address = None

    

    def _join(self, param):

        tokens = param.split(' ')
        if len(tokens) == 2:
            try:
                self.__address = (tokens[0], int(tokens[1]))
                print('Connecté à {}:{}'.format(*self.__address))

            except OSError:
                print("Erreur lors de l'envoi du message.")

    

    def _send(self, param):

        if self.__address is not None:
            try:
                message = param.encode()
                totalsent = 0
                while totalsent < len(message):
                    sent = self.__s.sendto(message[totalsent:], self.__address)
                    totalsent += sent

            except OSError:
                print('Erreur lors de la réception du message.')

    

    def _receive(self):

        while self.__running:
            try:
                data, address = self.__s.recvfrom(1024)
                print("[{}] {}".format(address, data.decode()))

            except socket.timeout:
                pass

            except OSError:
                return






class EchoServer:

    def __init__(self):
        self.__s = socket.socket()
        self.__s.bind(("0.0.0.0", PORT))

        

    def run(self):

        self.__s.listen()
        while True:
            client, addr = self.__s.accept()

            try:
                print(self._receive(client).decode())
                client.close()

            except OSError:
                print('Erreur lors de la réception du message.')

    

    def _receive(self, client):
        chunks = []
        finished = False
        while not finished:
            data = client.recv(1024)
            chunks.append(data)
            finished = data == b''

        return b''.join(chunks)





class EchoClient:

    def __init__(self, message, serverIP="127.0.0.1"):
        self.__message = message
        self.__s = socket.socket()
        self.serverIP = serverIP

    

    def run(self):

        try:
            self.__s.connect((self.serverIP, PORT))
            self._send()
            self.__s.close()

        except OSError:
            print('Serveur introuvable, connexion impossible.')

    

    def _send(self):
        totalsent = 0
        msg = self.__message
        try:
            while totalsent < len(msg):
                sent = self.__s.send(msg[totalsent:])
                totalsent += sent

        except OSError:

            print("Erreur lors de l'envoi du message.")



if __name__ == '__main__':

    # Server 

    if len(sys.argv) == 2 and sys.argv[1] == 'server':

        EchoServer().run()

    elif len(sys.argv) > 2 and sys.argv[1] == 'client':
        if len(sys.argv) == 3:

            EchoClient(sys.argv[2].encode()).run()

        else:

            EchoClient(sys.argv[3].encode(), sys.argv[2]).run()

    # Chat 

    if len(sys.argv) == 3:
        Chat(sys.argv[1], int(sys.argv[2])).run()

    elif len(sys.argv) == 2:
        Chat(port=int(sys.argv[1])).run()

    else:
        Chat().run()