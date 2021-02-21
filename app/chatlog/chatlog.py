from datetime import datetime
from pathlib import Path
import pandas as pd

DATE_FORMAT = "%Y %m %d"
TIME_FORMAT = "%H:%M:%S"
DATE_COMMA_TIME_FORMAT = f'{DATE_FORMAT},{TIME_FORMAT}'

def find_logfile(room, start_fresh=False):
    app_dir = Path(__file__).resolve().parent.parent
    log_dir = app_dir / 'logs'
    if not log_dir.exists():
        log_dir.mkdir()
    log_file = log_dir / f'{room}.log'
    if not log_file.exists() or start_fresh:
        f = open(str(log_file), "w")
        header = 'date,time,user,message\n'
        f.write(header)
        f.close()
    return log_file


def log_chat(room, user, message):
    log_file = find_logfile(room)
    f = open(str(log_file), "a")
    now = datetime.now()
    date_time = now.strftime(DATE_COMMA_TIME_FORMAT)
    message = str(message).replace(',', ';') # replace comma in case it message up csv
    log_line = f'{date_time},{str(user)},{message}'
    f.write(log_line + '\n')
    f.close()


def load_conversation(room, start_fresh=False):
    log_path = find_logfile(room, start_fresh)
    log = None
    if log_path.exists():
        log_file = str(find_logfile(room))
        mydateparser = lambda x: pd.datetime.strptime(x, TIME_FORMAT)
        log = pd.read_csv(log_file, parse_dates=['time'], date_parser=mydateparser)
    return log
