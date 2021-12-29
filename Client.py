# Import:
from struct import *
from socket import *
import sys
import select
import termios
import tty

# Defines:
COOKIE_BYTES = 4
TYPE_BYTES = 1
TCP_PORT_BYTES = 2
COOKIE_KEY = 0xabcddcba
OFFER_MSG_TYPE = 0x2
SECOND = 1
BYTE = 1
ENDIAN = 'big'
MAX_BUF_SIZE = 1024
TIMEOUT = 10

# Global Variables:
client_name = "Hackathon of bytes"
clientIP = ''
clientPort = 13117

# Function to color the text that we print to the screen
# The coloring format: first {} - red, second {} - green, third {} - blue, forth {} - the text to color
def colored(r, g, b, text):
    return "\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(r, g, b, text)


# Wait for Offer message from one of the available servers
def look_for_server():
    try:
        clientSocket = socket(AF_INET, SOCK_DGRAM)  # create UDP socket
        clientSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        clientSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1) 
        clientSocket.bind((clientIP, clientPort))
        server_message, server_address = clientSocket.recvfrom(MAX_BUF_SIZE)  # receive message from server
        return server_message, server_address[0]
    
    except KeyboardInterrupt:
        print(colored(247, 21, 37, "Good bye :)"))
        quit()

    except:
        print(colored(255, 0, 0, "Something went wrong with the UDP connection."))


def check_message_details(cookie, type, server_tcp_port):
    flag = False

    if (cookie != COOKIE_KEY):
        print(colored(238, 30, 30, "Received message with wrong cookie. Keep waiting for offers \n"))

    elif (type != OFFER_MSG_TYPE):
        print(colored(238, 30, 30, "Received message with wrong type. Keep waiting for offers \n"))

    else:
        flag = True

    return server_tcp_port, flag


# Check if the received UDP message is a legal offer message
def check_valid_message(message):
    cookie = None
    type = None
    server_tcp_port = None

    try:
        cookie, type, server_tcp_port = unpack('=IbH', message)
        return check_message_details(cookie, type, server_tcp_port)
    except:
        pass

    try:
        cookie, type, server_tcp_port = unpack('IbH', message)
        return check_message_details(cookie, type, server_tcp_port)
    except:
        pass

    try:
        cookie, type, server_tcp_port = unpack('>4sbH', message)
        return check_message_details(cookie, type, server_tcp_port)
    except:
        pass

    try:
        cookie, type, server_tcp_port = unpack('<4sbH', message)
        return check_message_details(cookie, type, server_tcp_port)
    except:
        pass

    return None, False
    

# If the UDP offer message has the correct format, then connect to the offering server
def connect_to_server(server_ip_address, server_tcp_port):
    try:
        print(colored(197, 39, 229, "Received offer from " + server_ip_address + ", attempting to connect..."))
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect((server_ip_address, server_tcp_port))
        clientSocket.send((client_name + '\n').encode()) # Send the team name to the server with \n in the end.
        start_game_message = clientSocket.recv(MAX_BUF_SIZE) # Receive game starting message and question
        print(start_game_message.decode())  # TODO: take care of exceptions

        # The selctor knows to do both receiving messages from the server and recieve input from the keyboard
        read_sockets = [sys.stdin, clientSocket]
        old_info_stdin = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
        readable_sockets = select.select(read_sockets, [], [])[0]
        if readable_sockets[0] is sys.stdin: # If we need to read input from the keyboard
            # TODO: check if need to support messages before server welcom message

            user_answer = sys.stdin.read(BYTE) # Read one digit in a non blocking way
            print(colored(242, 155, 26, user_answer)) # Print the digit to the screen

            if (user_answer.isdigit()): # If the input is really a digit
                clientSocket.send(user_answer.encode("utf-8")) # Send the input to the answer as it's value and not in ascii
        # else:
        #   server_message = clientSocket.recv(1024)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_info_stdin)

        game_results_message = clientSocket.recv(MAX_BUF_SIZE) # Get the game result from the server
        print(colored(25, 239, 25, game_results_message.decode()))

        print(colored(58, 210, 120, "Server disconnected, listening for offer requests..."))
    
    except KeyboardInterrupt:
        print(colored(247, 21, 37, "Good bye :)"))
        quit()

    except:
        print(colored(255, 0, 0, "Somthing went wrong with the TCP connection."))

    finally:
        clientSocket.close() # close TCP socket

def main():
    print(colored(81, 219, 233, 'Welcome to the Game, client! :)'))
    print(colored(42, 115, 234, "Team name: " + client_name))
    print(colored(236, 242, 8, "Client started, listening for offer requests..."))

    while True:
        
        server_message, server_ip_address = look_for_server()
        # print("Server ip: " + server_ip_address)
        # print(server_message)

        server_tcp_port, legal_message = check_valid_message(server_message)
        if (legal_message):
            connect_to_server(server_ip_address, server_tcp_port)


if __name__ == "__main__":
    main()