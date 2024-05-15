import network, threading

t = threading.Thread(target=network.main)
t.start()

while True:
    input()
    print(network.send('localhost', 8000, 'Hello, world!'))

