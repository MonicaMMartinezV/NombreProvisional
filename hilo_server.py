import socket
import threading

# Dictionary to store client information
client_dic = {}

def com_client(client_addr):
    """
    Handle communication with a client.

    This function sends a 'Connected' message to the client, retrieves the user
    name associated with the client address, and continues communication with 
    the client until an exception occurs.

    Parameters:
    - client_addr (tuple): The address of the client.

    Returns:
    - None
    """
    
    # Send a 'Connected' message to the client
    client_dic[client_addr]['Socket'].send('Connected'.encode())

    # Get the user name associated with the client address
    user_name = user_client(client_addr)

    # Continue communication with the client until an exception occurs
    while True:
        try:
            # Receive message from the client
            message_recv = client_dic[user_name]['Socket'].recv(1024).decode()

            # Append received message to client's message list
            client_dic[user_name]['Messages'].append(message_recv)
            
            # Broadcast the received message to other clients
            broadcast_message(user_name, message_recv)
        except Exception as e:
            # Handle connection error and remove client from dictionary
            delete_client(user_name)
            print(f"Connection error: {e}")
            break

def broadcast_message(user_name, message):
    """
    Broadcast a message from a user to all other clients.

    This function sends a message from a user to all other clients connected 
    to the server, prepending the user's name to the message.

    Parameters:
    - user_name (str): The name of the user sending the message.
    - message (str): The message to be broadcasted.

    Returns:
    - None
    """
    for client_un in client_dic:
        # Check if the client is not the user who sent the message
        if client_un != user_name:
            # Prepend the user's name to the message
            message = f"{user_name}: {message}"
            # Send the message to the client
            client_dic[client_un]['Socket'].send(message.encode())

def delete_client(user_name):
    """
    Delete a client from the client dictionary.

    This function removes a client from the client dictionary based on their 
    user name.

    Parameters:
    - user_name (str): The name of the client to be deleted.

    Returns:
    - None
    """
    for client_un in client_dic:
        # Check if the current client's user name matches the specified user 
        # name
        if client_un == user_name:
            # Remove the client from the dictionary
            client_dic.pop(user_name)
            # Exit the loop since the client has been found and removed
            break

def user_client(client_addr):
    """
    Retrieve user name associated with client address and update client 
    dictionary.

    This function retrieves the user name associated with a client address
    from the client dictionary. It then updates the client dictionary by 
    removing the entry with the client address as key and adding a new entry
    with the user name as key and the previous client data as value.

    Parameters:
    - client_addr (tuple): The address of the client.

    Returns:
    - str: The user name associated with the client address.
    """
    # Receive user name from client
    user_name = client_dic[client_addr]['Socket'].recv(1024).decode()
    # Remove client data from dictionary using client address as key and store
    # it
    client_data = client_dic.pop(client_addr)
    # Add client data to dictionary using user name as key
    client_dic[user_name] = client_data
    # Return the user name
    return user_name

def server_connection():
    """
    Establish and manage connections with clients.

    This function creates a server socket, binds it to a specific address and
    port, and listens for incoming connections. When a client connects, it 
    prints a message indicating the connection and adds the client information 
    to the client dictionary. It also starts a new thread to handle 
    communication with the client.

    Parameters:
    - None

    Returns:
    - None
    """
    # Create a socket object
    socket_server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )
    
    # Bind the socket to the server address and port
    socket_server.bind(('127.0.0.1', 5000))
    # Listen for incoming connections with a maximum of 4 connections in the
    # queue
    socket_server.listen(4)

    print("Waiting for connections...")

    while True:
        try:
            # Accept a client connection
            client_sock, client_addr = socket_server.accept()
            # Print connection message
            print(f"Connection with: {client_addr}")
            # Add client information to the client dictionary
            client_dic[client_addr] = {
                'Socket': client_sock,
                'Messages': []
            }
            # Start a new thread to handle communication with the client
            client_thrd = threading.Thread(
                target=com_client,
                args=(client_addr,)
            )

            client_thrd.start()
        except KeyboardInterrupt:
            # Close the server socket if interrupted
            socket_server.close()
            break
        except Exception as e:
            print(f"Connection error: {e}")
            break

if __name__ == '__main__':
    # Start the server connection
    server_connection()