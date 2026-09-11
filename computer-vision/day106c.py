from day106b import run_diagnostic_crowd_test

if __name__ == "__main__":
    print("STRICT PROTOCOL FOR THIS TEST:")
    print("1. Decide the exact sequence BEFORE starting (e.g. 'all 4 cross down once, together, then stop').")
    print("2. Have ONE person (not in the test) count out loud each real crossing as it happens.")
    print("3.Write down the real count immediately after, before checking the log.")
    print("4. Only then compare against what the script reports.\n")
    input("Press Enter when your group has agreed on the exact sequence and is ready...")

    run_diagnostic_crowd_test(duration_seconds=30)