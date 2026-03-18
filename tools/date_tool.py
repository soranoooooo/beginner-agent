from datetime import datetime

def get_today_date():
    return datetime.now().strftime("%Y-%m-%d")