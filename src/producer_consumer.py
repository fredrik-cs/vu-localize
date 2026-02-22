import time

from iw_interpret import Cell


def producer(queue):
    # Trigger and dump scan results for main thread to consume when necessary
    while True:
        unfiltered_cells = []
        sleep_duration = 0.01

        for i in range(10):
            Cell.trigger_scan()
            cell_dump = Cell.dump_scan()
            unfiltered_cells.append(cell_dump)
            time.sleep(sleep_duration)

        good_cells = list(filter(lambda cell: cell.signal>=-67, unfiltered_cells))
        
        queue.put(good_cells)

def consumer(queue):
    # Transform scan results to distances and then locations
    message = queue.get()
    print(message)
        
