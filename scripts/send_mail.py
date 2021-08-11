from datetime import datetime
from news import naverapi


now = datetime.now()
current_time = str(now.hour).zfill(2) + ':' + str(now.minute).zfill(2)

naverapi.send_email_by_schedule(current_time)
