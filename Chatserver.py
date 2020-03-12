import socket 

s= socket.socket()
host = '0.0.0.0'
port = 5555

s.bind(('0.0.0.0',5555))
s.settimeout
s.listen()
print(f'Listen on {host}:{port}')


def reply(response,client)  :
    client.send(json.dumps(response))
    client.close()


def connect(data,client): 
    clients[data['nick']] = data['adress']
    reply({'ok': True}, client)

def getList (data, client) : 
    reply(clients, client)
    client.close()
def error(client) : 
    reply ({'error' : True })


while True : 
    try : 
        client, addre =s.accept()      # ici on déballe le tuple accept dans client et adrr 
        data = s.recv(1024).decode()
        if data['cmd'] == 'connect' : 
            connect(data)
        elif data['cmd'] == 'list' : 
            getList(data, client)
    except socket.timeout:

    pass 