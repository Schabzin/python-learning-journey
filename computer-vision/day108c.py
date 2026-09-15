from day108b import BidirectionalCounterV3

if __name__ == "__main__":
    LINE_Y = 460

    print("=== REGRESSION TEST: Standing sway near the line (Day 104's original bug) ===")
    counter = BidirectionalCounterV3(line_y=LINE_Y, buffer_zone=15)

    sway_sequence = [
        {0: (100, 455)},
        {0: (100, 465)},
        {0: (100, 458)},
        {0: (100, 462)},
        {0: (100, 456)},
        {0: (100, 464)},
        {0: (100, 459)},
        {0: (100, 461)},
    ]

    for frame_num, tracked_objects in enumerate(sway_sequence):
        in_count, out_count, net = counter.update(tracked_objects)
        direction = counter.last_crossing_direction
        cy = tracked_objects.get(0, ('-', '-'))[1]
        print(f"Frame {frame_num}: cy={cy}, IN={in_count} OUT={out_count} NET={net}, "
              f"crossing_event={direction}")

    print(f"\nFinal: IN:{counter.in_count}, OUT={counter.out_count}, NET={counter.net_occupancy}")
    print("If NET is high (e.g. several IN/OUT pairs) from pure standing sway, that's a regression.")