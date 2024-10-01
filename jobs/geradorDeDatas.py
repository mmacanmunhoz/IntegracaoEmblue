

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

init_date = datetime.strptime('01/01/2022 00:00:00', "%d/%m/%Y %H:%M:%S")
fin_date = datetime.strptime('01/09/2024 00:00:00', "%d/%m/%Y %H:%M:%S")

aux_date = fin_date

datas = list([])

while aux_date > init_date:
    textDates =  ';' + (aux_date - timedelta(seconds=1)).strftime("%Y-%m-%d %H:%M:%S")
    aux_date = (aux_date - relativedelta(months=1))
    tempDate = aux_date
    textDates = tempDate.strftime("%Y-%m-%d %H:%M:%S") + textDates

    datas.append(textDates)

with open('data/dates.txt', mode='w') as file:
    file.writelines(list(map(lambda x: f"{x}\n", datas)))