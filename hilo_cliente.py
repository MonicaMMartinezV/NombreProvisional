import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

# Create a socket object to handle the server connection
socket_server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

try:
    # Connect to the server to an local IP for testing
    socket_server.connect(('127.0.0.1',5000))
except:
    print("Server is down")
    exit()

# Receive a 'Connected' response from the server
print(socket_server.recv(1024).decode())

# Get from the user a nickname
user_name = input("Enter your username: ")

# Send the username to the server
socket_server.send(user_name.encode())

def receive_messages():
    """
    Receive and display messages from the server into the GUI.

    Parameters:
    - None

    Returns:
    - None

    This function continuously receives messages from the server and displays
    them in the chat window.
    
    If the server disconnects, it shows a messagebox informing the user and 
    closes the application.
    """
    try:
        while True:
            try:
                # Receive message from the server
                message_recv = socket_server.recv(1024).decode()
                
                # Check if message received is empty (indicating server 
                # disconnection)
                if not message_recv:
                    messagebox.showinfo("Server disconnected",
                                        "The app will close.")
                    exit()
                
                # Enable the chat window for editing, insert the received message,
                # then disable editing again
                chat_window.config(state=tk.NORMAL)
                chat_window.insert(tk.END,
                                message_recv + '\n')
                chat_window.config(state=tk.DISABLED)
                
                # Scroll the chat window to show the latest message
                chat_window.yview(tk.END)
            except KeyboardInterrupt:
                break
            
    # Handle BrokenPipeError (raised when socket is closed abruptly)
    except BrokenPipeError:
        print("Error")
        
    # Ensure the socket is closed, even if an error occurs
    finally:
        socket_server.close()

def send_messages(event=None):
    """
    Send a message to the server and display it in the chat window.

    Parameters:
    - event (tk.Event, optional): The event that triggered the function.
      Default is None.

    Returns:
    - None

    This function retrieves the message entered by the user from the message 
    entry field. If the message is not empty, it inserts the message in the 
    chat window with the prefix "You:".
    
    The chat window is then disabled to prevent user input, scrolled to show 
    the latest message, and the message entry field is cleared.
    
    Finally, the message is sent to the server after encoding it.
    """
    # Get the message from the GUI when clicking the button or with an enter 
    # from keyboard
    message_val = message_entry.get()
    
    if message_val:
        # Enable the chat window for editing, insert the message, then disable
        # editing
        chat_window.config(state=tk.NORMAL)
        chat_window.insert(tk.END,
                           "You: " + message_val + '\n')
        chat_window.config(state=tk.DISABLED)
        
        # Scroll the chat window to show the latest message
        chat_window.yview(tk.END)
        
        # Clear the message entry field
        message_entry.delete(0, tk.END)
        
        # Send the message to the server after encoding it
        socket_server.send(message_val.encode())

def on_closing():
    """
    Handle the closing event of the main window.

    Parameters:
    - None

    Returns:
    - None

    This function is called when the user attempts to close the main window.
    It destroys the main window, terminates the application, and exits the 
    program.
    """
    main_window.destroy()
    exit()

# Create the main window
main_window = tk.Tk()

# Set the title of the main window
main_window.title("ThreadsChatPy")

# Disable window resizing
main_window.resizable(False, False)

# Set window in front of other apps
main_window.attributes("-topmost", True)

# Define the action when the window is closed
main_window.protocol("WM_DELETE_WINDOW", on_closing)

# Create a scrolled text widget for displaying chat messages
chat_window = scrolledtext.ScrolledText(main_window,
                                        state=tk.DISABLED,
                                        width=50,
                                        height=20)
chat_window.grid(row=0,
                 column=0,
                 columnspan=2,
                 padx=10, 
                 pady=10)

# Create an entry widget for typing messages
message_entry = tk.Entry(main_window,
                         width=40)
message_entry.grid(row=1,
                   column=0,
                   padx=10,
                   pady=10)

# Bind the Enter key to the send_messages function
message_entry.bind("<Return>", send_messages)  

# Create a button for sending messages
send_button = tk.Button(main_window, text="Send", command=send_messages)
send_button.grid(row=1, column=1, padx=10, pady=10)

# Create a thread for receiving messages from the server
recieve_thread = threading.Thread(
    target=receive_messages
)

# Start the receive thread
recieve_thread.start()

# Start the main event loop to display the window and handle user interactions
main_window.mainloop()