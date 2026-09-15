from day103 import KalmanBoxTracker

class BidirectionalCounterV3:
    def __init__(self, line_y, buffer_zone=15):
        self.line_y = line_y
        self.buffer_zone = buffer_zone
        self.previous_positions = {}
        self.last_direction = {}
        self.in_count = 0
        self.out_count = 0

    @property
    def net_occupancy(self):
        return self.in_count - self.out_count

    def update(self, tracked_objects):
        self.last_crossing_id = None
        self.last_crossing_direction = None

        for object_id, (cx, cy) in tracked_objects.items():
            if object_id not in self.last_direction:
                self.last_direction[object_id] = None

            if object_id in self.previous_positions:
                prev_cy = self.previous_positions[object_id]

                crossed_down = prev_cy < self.line_y <= cy
                crossed_up = prev_cy > self.line_y >= cy

                if crossed_down and self.last_direction[object_id] != "IN":
                    self.in_count += 1
                    self.last_direction[object_id] = "IN"
                    self.last_crossing_id = object_id
                    self.last_crossing_direction = "IN"

                elif crossed_up and self.last_direction[object_id] != "OUT":
                    self.out_count += 1
                    self.last_direction[object_id] = "OUT"
                    self.last_crossing_id = object_id
                    self.last_crossing_direction = "OUT"

            self.previous_positions[object_id] = cy

        return self.in_count, self.out_count, self.net_occupancy

if __name__ == "__main__":
    LINE_Y = 460

    print("=== RETEST: Same sequence that failed in Session 1, now with the fix ===")
    counter = BidirectionalCounterV3(line_y=LINE_Y, buffer_zone=15)

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

    for frame_num, tracked_objects in enumerate(sequence):
        in_count, out_count, net = counter.update(tracked_objects)
        direction = counter.last_crossing_direction
        crossing_id = counter.last_crossing_id
        cy = tracked_objects.get(0, ('-', '-'))[1]
        print(f"Frame {frame_num}: cy={cy}, IN={in_count} OUT={out_count} NET={net}, "
              f"crossing_event={direction} by ID {crossing_id}")

    print(f"\nFinal: IN={counter.in_count}, OUT={counter.out_count}, NET={counter.net_occupancy}")