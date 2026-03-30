
--------------- INGEST ---------------

# Vai puxar os processos do dataJud
- Enviar para api todos os processos encontrados

--------------- API ---------------
# Filtrar os processos faltantes
Verificamos processos aonde o ID nao existe ou entao
a data de atualização do processo enviado é mais recente que a armazenada no banco

# Criar os processos faltantes

# Retornar os processos que conseguiram ser criados para que passem para proxima etama

--------------- INGEST ---------------

# Vai enviar o pipeline extração PDF
1. Processos retornados pela API
2. Processos iniciais que ainda não existem no bucket