import zmq
import csv

# ZeroMQ Setup
context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.connect("tcp://localhost:5555")  # Connect to the server's socket

# Listening for log messages
with open('crossing_log.csv', 'a', newline='') as csv_file:
    while True:
        message = socket.recv_string()  # Receive log data
        csv_file = open('crossing_log.csv', 'a', newline='')
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(message.split(", "))  # Split the message and write to CSV
        csv_file.close()
        print("LOG WRITTEN => ", message)

# Cleanup

context.term()
