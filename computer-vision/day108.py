from day102c import BidirectionalCounterV2

def simulate_positions(counter, id_positions_sequence):
    """
    id_positions_sequence: list of {object_id: (cx, cy)} dicts, one per
    simulated 'frame'. Feeding hand-built fake positions means we can test
    ONLY the counter's logic, with zero interference from YOLO/SORT noise,
    timing, or camera issues -- the exact things that made live testing
    hard to interpret this week.
    """
    for frame_num, tracked_objects in enumerate(id_positions_sequence):
        in_count, out_count, net = counter.update(tracked_objects)
        direction = counter.last_crossing_direction
        crossing_id = counter.last_crossing_id
        print(f"Frame {frame_num}: cy={tracked_objects.get(0, ('-', '-'))[1]}, "
              f"IN={in_count} OUT={out_count} NET={net}, "
              f"crossing_event={direction} by ID {crossing_id}")

if __name__ == "__main__":
    LINE_Y = 460

    print("=== TEST 1: Simple IN then OUT for one person (ID 0) ===")
    counter = BidirectionalCounterV2(line_y=LINE_Y, release_distance=100)
    sequence = [
        {0: (100, 300)},
        {0: (100, 380)},
        {0: (100, 470)},
        {0: (100, 550)},
        {0: (100, 550)},
        {0: (100, 470)},
        {0: (100, 440)},
        {0: (100, 350)},
    ]
    simulate_positions(counter, sequence)

    print(f"\nFinal: IN={counter.in_count}, OUT={counter.out_count}, NET={counter.net_occupancy}")