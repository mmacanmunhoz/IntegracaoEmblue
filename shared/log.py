
from datetime import datetime

file = f"_logs/log{datetime.now().strftime("%Y%m%d%H%M%S")}.txt"

def log(message):
    print(message)
    with open(file, 'a') as f:
        dateStr = datetime.now().strftime("%d/%m %H:%M") 
        f.write(dateStr + ' - ' + message + '\n')