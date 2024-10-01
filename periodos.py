

from datetime import datetime

class PeriodoService:

    def __init__(self) -> None:
        self.datas = list()
        self.lines = list()
        with open('data/dates.txt', mode='r') as file:
            self.lines = list(map(lambda d : d.replace('\n',''), file.readlines()))
            
        for l in self.lines:
            split = l.split(';')
            start = datetime.strptime(split[0],'%Y-%m-%d %H:%M:%S')
            end = datetime.strptime(split[1],'%Y-%m-%d %H:%M:%S')
            self.datas.append([start,end])
                    
        pass
    
    def prox(self):
        if(len(self.datas)>0):
            datas = self.datas[0]
            return datas
        return None
    
    def salvar(self):
        self.datas = self.datas[1:]
        self.lines = self.lines[1:]
        with open('data/dates.txt', mode='w') as file:
            file.writelines(list(map(lambda x: f"{x}\n", self.lines)))

    def porcentagem(self):
        with open('data/dates.txt', mode='r') as file:
            return 100 - (100 * len(file.readlines()) / 30)