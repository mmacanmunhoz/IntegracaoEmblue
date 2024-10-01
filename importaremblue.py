

from mvx.mvx_service import *
from emblue.emblue_service import *
from shared.log import *


mvx_service = MvxService()

mvx_clientes = list(filter(lambda x: len(x.email_cliente) > 0 and x.tipo == 'c' and x.touched == True, mvx_service.LISTA_MVXCLIENTES)) #

usuarios_integrados = 0
usuarios_nao_integrados = 0
total = len(mvx_clientes)
    
emblue = EmblueService("R08FuPOT-FUpQV-2HYbH-utu69rLiHQ","emblue.mundoverde@hagaze.com.br","aT.q86zMhgR2eFF@")
if isinstance(emblue.token_res, str):
    log("Erro no token da emblue")
    log(emblue.token_res)
    quit()

for mvx_cliente in mvx_clientes:
    res = emblue.atualizar_contato(mvx_cliente)
    if res == True:
        usuarios_integrados += 1
        log(f'Usuarios integrados na emblue: {usuarios_integrados}/{total} - cod: {mvx_cliente.cod_cliente} - id: {mvx_cliente.emblue_email_id}')
    else:
        usuarios_nao_integrados += 1
        log(f'Falha de integração na emblue: {usuarios_nao_integrados} - cod: {mvx_cliente.cod_cliente}')

mvx_service.salvar_em_memoria(True)
