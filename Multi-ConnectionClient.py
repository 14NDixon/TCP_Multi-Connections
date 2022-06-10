# This code establishes a multi-connection client for use with the ULI Tech Demo
# Based of the source https://realpython.com/python-sockets/#multi-connection-server
import sys
import socket
import selectors
import types
import time

sel = selectors.DefaultSelector()


# THIS BIT OF CODE WILL GO IN THE INITIALIZATION
hostName_home = "10.0.0.234"
hostName_Laptop_USU = "144.39.251.168"
hostName_Desktop_USU_Nolan = "129.123.61.202"
portNumber = 7001
directory = 'C:\\Users\\Nolan Dixon\\AppData\\Roaming\\flightgear.org\\Export\\'
host, port, num_conns = hostName_Desktop_USU_Nolan, portNumber, 1



def send_data(host, port, num_conns):
    try:
        while True:
            events = sel.select(timeout=1)
            if events:
                for key, mask in events:
                    # Check FlightGear for the Most Recent Update
                    lastRow = check_for_update()
                    messages = [bytes(str(lastRow), "utf-8")]
                    # Service Connection
                    service_connection(key, mask)
            # Check for a socket being monitored to continue.
            if not sel.get_map():
                break
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
    # finally:
    #     sel.close()


def check_for_update():
    with open(directory + 'FlightLog_Waypoints.csv', newline='') as csvfile:
        data = csvfile.readlines()
        lastRow = data[-1]
    csvfile.close()
    return lastRow


def start_connections(host, port, num_conns, messages):
    server_addr = (host, port)
    for i in range(0, num_conns):
        connid = i + 1
        print(f"Starting connection {connid} to {server_addr}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(server_addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        data = types.SimpleNamespace(
            connid=connid,
            msg_total=sum(len(m) for m in messages),
            recv_total=0,
            messages=messages.copy(),
            outb=b"",
        )
        sel.register(sock, events, data=data)
        # Register registers a file object for selection monitoring it for I/O events.


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            print(f"Received {recv_data.decode('utf-8')!r} from connection {data.connid}")
            data.recv_total += len(recv_data)
        if not recv_data or data.recv_total == data.msg_total:
            print(f"Closing connection {data.connid}")
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)

        if data.outb:
            print(f"Sending {data.outb!r} to connection {data.connid}")
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]


def run():
    while True:
        lastRow = check_for_update()
        messages = [bytes(str(lastRow), "utf-8")]
        start_connections(host, int(port), int(num_conns), messages)
        send_data(hostName_Desktop_USU_Nolan, portNumber, 1)
        time.sleep(5)



run()


# def run():
#     initialize_FlightSim_client()
#
#     while FlightSim:
#         try:
#             while True:
#                 events = sel.select(timeout=1)
#                 if events:
#                     for key, mask in events:
#                         # Check FlightGear for the Most Recent Update
#                         lastRow = check_for_update()
#                         messages = [bytes(str(lastRow), "utf-8")]
#                         # Service Connection
#                         service_connection(key, mask)
#                 # Check for a socket being monitored to continue.
#                 if not sel.get_map():
#                     break
#         except KeyboardInterrupt:
#             print("Caught keyboard interrupt, exiting")
#
#         finally:
#             sel.close()
#     # NEED TO MAKE A BREAKOUT POINT



# # BEGIN INITIAL RUN
# lastRow = check_for_update()
# messages = [bytes(str(lastRow), "utf-8")]
# start_connections(host, int(port), int(num_conns))
#
#
# # I BELIEVE THIS PART IS THE BIT OF CODE THAT WILL GO WITHIN A FUNCTION CALL TO GET MORE DATA
# try:
#     while True:
#         events = sel.select(timeout=1)
#         if events:
#             for key, mask in events:
#                 # Check FlightGear for the Most Recent Update
#                     lastRow = check_for_update()
#                     messages = [bytes(str(lastRow), "utf-8")]
#                     # Service Connection
#                     service_connection(key, mask)
#         # Check for a socket being monitored to continue.
#         if not sel.get_map():
#             break
# except KeyboardInterrupt:
#     print("Caught keyboard interrupt, exiting")
# finally:
#     sel.close()
