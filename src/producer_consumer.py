import time
from queue import Queue

from src.iw_interpret import Cell

AS_SLEEP_DURATION = 0.01
AS_ITERATIONS = 10

def producer(queue: Queue, band = []):
    # Trigger and dump scan results for main thread to consume when necessary
    while True:
        unfiltered_cells: list[Cell] = []

        for i in range(AS_ITERATIONS):
            Cell.trigger_scan(band)
            cell_dump = Cell.dump_scan()
            unfiltered_cells.extend(cell_dump)
            time.sleep(AS_SLEEP_DURATION)

        good_cells = list(filter(lambda cell: cell.signal>=-67, unfiltered_cells))
        
        queue.put(good_cells)

def consumer(queue: Queue):
    # Transform scan results to distances and then locations
    while True:
        
        try:
            message = queue.get()
            print(message)
            time.sleep(AS_ITERATIONS * AS_SLEEP_DURATION)
        except:
            time.sleep(AS_ITERATIONS * AS_SLEEP_DURATION)
        
