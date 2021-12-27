from struct import *
from socket import *

client_name = "Team 1\n"
clientIP = ''
clientPort = 13117
COOKIE_BYTES = 4
TYPE_BYTES = 1
TCP_PORT_BYTES = 2
COOKIE_KEY = 0xabcddcba
OFFER_MSG_TYPE = 0x2

# Wait for Offer message from one of the servers
def look_for_server():
    clientSocket = socket(AF_INET, SOCK_DGRAM) # create UDP socket
    clientSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    clientSocket.bind((clientIP, clientPort))
    server_message, server_address = clientSocket.recvfrom(2048) # receive message from server
    clientSocket.close() # close UDP connection
    return server_message,server_address[0]

# Check if the received UDP message is a legal offer message
def check_valid_message(message):
    flag = False
    cookie, type, server_tcp_port = unpack('!IBh', message)
    if(cookie != COOKIE_KEY):
        print("Received message with wrong cookie. Keep waiting for offers \n")

    elif(type != OFFER_MSG_TYPE):
        print("Received message with wrong type. Keep waiting for offers \n")

    else: flag = True
    
    return server_tcp_port, flag;


def connect_to_server(server_ip_address, server_tcp_port):
    print("Received offer from " + server_ip_address + ", attempting to connect...")
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((server_ip_address,server_tcp_port))
    clientSocket.send(client_name.encode())
    welcome_message = clientSocket.recv(1024)
    print (welcome_message) # TODO: take care of newline and exceptions

    
    clientSocket.close()


def main():

    while True:
        print("Client started, listening for offer requests...")
        server_message, server_ip_address = look_for_server()
        
        print("Server ip: " + server_ip_address)
        print(server_message)

        server_tcp_port, legal_message = check_valid_message(server_message)
        if(legal_message):
            connect_to_server(server_ip_address, server_tcp_port)


if __name__ == "__main__":
    main()