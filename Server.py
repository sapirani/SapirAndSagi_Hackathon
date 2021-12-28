# Import:
import threading
import select
from socket import *
from struct import *
import time
import random

# Defines:
SECOND = 1
BYTE = 1
ENDIAN = 'big'
MAX_BUF_SIZE = 1024
TIMEOUT = 10

# Global Variables:
serverIP = '172.1.0.10'
serverPort = 22222

UDP_broadcast_IP = '172.1.0.10'
UDP_destination_port = 13117
UDP_client_address = (UDP_broadcast_IP, UDP_destination_port)

is_in_game = False
question_bank = {"4 + 4" : 8,
                 "5 + 2 - 1" : 6,
                 "5 * 2 - 1" : 9,
                 "1 + 2 * 3" : 7,
                 "(1 + 1) * 2" : 4,
                 "3 + 4 + 1" : 8,
                 "2 + 4 - 3" : 3,
                 "1 + 1 + 1 * 0 + 1 + 1 + 1 + 1" : 6,
                 "4 + 3 - 2" : 5,
                 "4 * 4 / 2" : 8,
                 "(4 * 4) / 16" : 1,
                 "1 + 1 + 1 + 1 + 1 + 1 * 0 + 1 + 1" : 7,
                 "5 - 4 + 1" : 2,
                 "25 / 5" : 5,
                 "(10 + 10 + 10 + 10 + 10) / 10" : 5,
                 "2 + 2 + 2" : 6,
                 "3 + 0 + 3 * 0" : 3}

# Function to color the text that we print to the screen
# The coloring format: first {} - red, second {} - green, third {} - blue, forth {} - the text to color
def colored(r, g, b, text):
    return "\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(r, g, b, text)

# Build offer message
def get_broadcast_message():
    magic_cookie = 0xabcddcba
    message_type = 0x02
    server_port = serverPort
    sending_format = '!IBh' # The bytes format
    return pack(sending_format, magic_cookie, message_type, server_port)

# Send offer message over broadcast in UDP
def offer_udp():
    server_socket = socket(AF_INET, SOCK_DGRAM)
    server_socket.bind((serverIP, serverPort))

    while True:
        if not is_in_game: # If the server allready has 2 clients connected and the game started, don't look for new clients
            message = get_broadcast_message()
            server_socket.sendto(message, UDP_client_address)
        time.sleep(SECOND)

# Get random question from the question bank (questions dictionary)
def select_random_question():
    max_len = len(question_bank)
    question_number = random.randint(0,max_len - 1)
    return  list(question_bank)[question_number]

# Get the name of the winning team.
# If the first client answerd first and correctly, he wins.
# If the second client answerd first and correctly, he wins.
# Otherwise, it can be a draw or the other client wins.
def get_winner_name(socket_with_answer, first_client_socket, second_client_socket, first_player_name,
                    second_player_name, correct_answer):
    if socket_with_answer is first_client_socket: # The first client answered first
        if int.from_bytes(first_client_socket.recv(BYTE), ENDIAN) == correct_answer:
            return first_player_name # answer is correct
        else:
            return second_player_name # answer is incorrect

    else: # The second client answered first
        if int.from_bytes(second_client_socket.recv(BYTE), ENDIAN) == correct_answer:
            return second_player_name # answer is correct
        else:
            return first_player_name # answer is incorrect

# Starting the game after receiving two clients
def handle_clients(first_client_socket, second_client_socket):
    global is_in_game
    is_in_game = True
    first_player_name = first_client_socket.recv(MAX_BUF_SIZE).decode()
    second_player_name = second_client_socket.recv(MAX_BUF_SIZE).decode()

    # Select random question from the bank.
    selected_question = select_random_question()
    answer_to_the_question = question_bank.get(selected_question)
    message = """
    Quick Maths Is Starting!
    Player 1: {first_player_name}
    Player 2: {second_player_name}
    ================================ 
    Please answer the following question as fast as you can:
    {question}""".format(first_player_name=first_player_name,
                               second_player_name=second_player_name, question=selected_question)

    first_client_socket.send(message.encode())
    second_client_socket.send(message.encode())

    # The selector knows which client answered first.
    readable, _, _ = select.select([first_client_socket, second_client_socket], [], [], TIMEOUT)

    game_message = """
    Game over!
    The correct answer was {answer}!""".format(answer=answer_to_the_question)

    if len(readable) == 0: # If non of the clients answered, it's a draw.
        game_message += "\n    Game result: Draw\n"

    else: # Else, there is a winner to the game.
        winner = get_winner_name(readable[0], first_client_socket, second_client_socket,
                                 first_player_name, second_player_name, answer_to_the_question)
        game_message += "\n    Congratulations to the winner: {winner}\n".format(winner=winner)

    first_client_socket.send(game_message.encode())
    second_client_socket.send(game_message.encode())

    is_in_game = False # The game ended, start sending offer messages again.

# Recieve two clients over TCP
def receive_clients_tcp():
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind((serverIP, serverPort))
    server_socket.listen(1)

    while True:
        connection_socket_first_client, addr = server_socket.accept()
        connection_socket_second_client, addr = server_socket.accept()

        handle_clients(connection_socket_first_client, connection_socket_second_client)

        connection_socket_first_client.close()
        connection_socket_second_client.close()


def main():
    print(colored(81, 219, 233, 'Welcome to the Game server! :)'))
    print(colored(236,242,8, "Server started, listening on IP address " + serverIP))
    threading.Thread(target=offer_udp).start()
    threading.Thread(target=receive_clients_tcp).start()


if __name__ == "__main__":
    main()
