from struct import *
from socket import *
import sys
import select

client_name = "Team 1\n"
clientIP = '172.1.0.10'
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
    print (welcome_message.decode()) # TODO: take care of exceptions


    read_sockets = [sys.stdin, clientSocket]

    readable_sockets = select.select(read_sockets, [], [])[0]

    if readable_sockets[0] is sys.stdin: #TODO: check if need to support messages before sever welcom message
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
        user_answer = sys.stdin.read(1)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

        if (user_answer.isdigit()):
            digit_value = ord(user_answer) - ord('0')
            clientSocket.send(digit_value.to_bytes(1, 'big'))
    #else: 
     #   server_message = clientSocket.recv(1024)

    game_results_message = clientSocket.recv(1024)
    print (game_results_message.decode())
    
    clientSocket.close()


def main():

    while True:
        print("Client started, listening for offer requests...")
        server_message, server_ip_address = look_for_server()
        
        #print("Server ip: " + server_ip_address)
        #print(server_message)

        server_tcp_port, legal_message = check_valid_message(server_message)
        if(legal_message):
            connect_to_server(server_ip_address, server_tcp_port)


if __name__ == "__main__":
    main()