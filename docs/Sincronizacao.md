# Módulo de Sincronização e Triggers

## Objetivo

Garantir que todos os dados processados nas etapas anteriores do pipeline estejam sincronizados e processados corretamente, mesmo em casos de falhas intermediárias (ex: queda do worker-llm). O módulo deve permitir retomar o processamento a partir de qualquer estágio, sem perder dados ou gerar inconsistências.

## Pipeline Resumido

1. **Ingestão**: Busca dados no DataJud e retorna processos.
2. **PDF**: Processa PDFs dos processos.
3. **LLM**: Processa PDFs com LLM.
4. **API**: Envia resultados finais para a API.

## Problema

Se um worker intermediário falhar (ex: worker-llm), processos podem ficar "parados" em um estágio. O sistema atual considera que, ao chegar em um estágio, tudo anterior já está sincronizado, o que pode não ser verdade em caso de falhas.

## Solução Proposta

Criar um módulo de sincronização/triggers que:

- Permita rodar periodicamente (cron job) para verificar e retomar processamentos pendentes.
- Considere o estado dos arquivos/processos em cada camada (ex: PDFs no S3) para disparar o próximo estágio.
- Permita sincronizar a partir de qualquer estágio (ex: dos PDFs para o LLM, do LLM para a API).

## Funcionalidades

- **Trigger Manual e Automático**: Permitir execução manual ou via agendamento (cron).
- **Verificação de Consistência**: Checar se todos os itens do estágio anterior foram processados no estágio atual.
- **Reprocessamento**: Identificar e reprocessar itens pendentes ou falhos.
- **Logs e Alertas**: Registrar operações e alertar em caso de inconsistências ou falhas recorrentes.

## Exemplo de Fluxo

1. Sincronizador verifica PDFs no S3.
2. Para cada PDF sem resultado no LLM, dispara processamento no worker-llm.
3. Após processamento, verifica se resultado foi enviado para API; se não, dispara envio.
4. Repete o processo periodicamente ou sob demanda.

## Opções de Implementação

- **Cron Job**: Script Python ou serviço que roda periodicamente.
- **Trigger por Evento**: Opcionalmente, usar eventos do S3 ou filas para disparar sincronizações.
- **Dashboard/Monitoramento**: (Opcional) Interface para visualizar status e acionar sincronizações.

## Considerações

- O sincronizador deve ser idempotente (rodar múltiplas vezes não deve causar duplicidade).
- Deve ser possível parametrizar o estágio inicial da sincronização (ex: a partir dos PDFs, a partir dos resultados do LLM).
- Pensar em escalabilidade e tolerância a falhas.
