from datetime import datetime

def get_hour():
    return datetime.now().strftime("%Y-%m-%d-%H")
