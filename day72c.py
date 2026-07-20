from day72b import send_sms, build_target_alert

def run_daily_check():
    try:
        taxis = [
            {"plate": "MT64TP GP", "collected": 900, "target": 900, "phone": "+27742596321"},
            {"plate": "FG09KL GP", "collected": 700, "target": 900, "phone": ""},
            {"plate": "LK65XB GP", "collected": 500, "target": 900, "phone": +27831478523},
        ]

        for taxi in taxis:
            message = build_target_alert(taxi)
            if message and taxi["phone"]:
                send_sms(taxi["phone"], message)
            else:
                print(f"{taxi['plate']}: no alert sent (message={message}, phone={taxi['phone']!r})")

    except Exception as e:
        print(f"CRON JOB FAILED: {e}")

if __name__ == "__main__":
    run_daily_check()
    
                