def producer(queue):
    # Trigger and dump scan results for main thread to consume when necessary
    while True:
        message = "scan"
        queue.put(message)

def consumer(queue):
    # Transform scan results to distances and then locations
    message = queue.get()
    print(message)
        
