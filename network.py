import socket, select, importlib.util

HOSTNAME = 'localhost'

def send(name,port,message):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((name, port))
    client_socket.send(message.encode())
    try:
        response = client_socket.recv(1024).decode()
    except:
        response = None
    client_socket.close()
    return response

def execute(sender_address, port, data):
    function_location = assigned_ports[port]
    file_location = function_location[:function_location.find("\\")]
    function_name = function_location[function_location.find("\\")+1:]
    spec = importlib.util.spec_from_file_location("module", file_location)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if hasattr(module, function_name):
        function = getattr(module, function_name)
        return function(sender_address,data)
    else:
        raise AttributeError(f"Function not found in the end location")

def recieve():
    sockets = {}
    for port in ports:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOSTNAME, port))
        server_socket.listen(5)
        sockets[server_socket] = port

    print("Listening for connections...")

    while True:
        ready_to_read, _, _ = select.select(sockets.keys(), [], [])
        
        for ready_socket in ready_to_read:
            if ready_socket in sockets:
                client_socket, address = ready_socket.accept()
                port = sockets[ready_socket]
                print('\n-------------------[')
                print(f"Connection from {address} on port {port} established")
                data = client_socket.recv(1024).decode()
                if data:
                    response = execute(address, port, data)
                    print('Functon executed')
                    if response != None:
                        client_socket.sendall(response.encode())
                        print('Response sent')
                    client_socket.close()
                    print('Connection closed')
                else:
                    print('Connection closed by client')
                print(']-------------------\n')

def main():
    global assigned_ports
    assigned_ports = {}
    file = open("assigned_ports",'r')
    assigned_ports_array = file.readlines()
    file.close()
    for port in assigned_ports_array:
        new_port = port.rstrip('\n')
        function_address = new_port[:new_port.find(':')]
        function_port = int(new_port[new_port.find(':')+1:])
        print(function_address)
        print(function_port)
        assigned_ports[function_port] = function_address
    global ports
    ports = list(assigned_ports.keys())

    recieve()

if __name__ == "__main__":
    main()