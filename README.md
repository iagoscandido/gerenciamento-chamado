# GERENCIAMENTO DE CHAMADOS

## Stack

- Fastapi Standard
- Htmx 4.0
- Boostrap 5.0
- Sqlite3

## How to run

- uv run fastapi dev

## Anotations:

criação por etapas, começando pela estrutura basica, ignorando UX e UI e validações.
avance para proxima etapa após a etapa atual estar concluida e testada.

1. Etapa: criação da funcionalidade
2. Etapa: criação de regras de negócio
3. Etapa: implementação das regras de negócio
4. Etapa: implementação de melhoria visual, utilizando html semantico e bootstrap, o visual também deve ser responsivo.
5. Etapa: realizar testes manuais de fluxo.

sugira nomeação em inglês, baseado no contexto e em boas práticas.

- ticket(id, service_date, start_travel, start_tive, end_time, protocol, client, address, value, created_at, updated_at, status(open, on_travel, on_progress, finished), contratante)

Processo de criação de um ticket

para cada passo: criar uma query -> service -> route -> formulario.

1. criar chamado(registrando endereço, cliente, valor).
2. iniciar deslocamento(registrando o horário de saída).
3. iniciar atendimento(registrando horário de inicio do atendimento).
4. finalizar atendimento(registrando horário de finalização do atendimento).
5. Edição do chamado(registrando os campos que não foram preenchidos)

documentação htmx: https://raw.githubusercontent.com/bigskysoftware/htmx/v4.0.0/dist/skills/htmx-guidance.md

debug htmx: https://raw.githubusercontent.com/bigskysoftware/htmx/v4.0.0/dist/skills/htmx-debugging.md

## Flow

| Estado atual  | Operação             | Novo estado   |
| ------------- | -------------------- | ------------- |
| `OPEN`        | iniciar deslocamento | `ON_TRAVEL`   |
| `ON_TRAVEL`   | iniciar atendimento  | `ON_PROGRESS` |
| `ON_PROGRESS` | finalizar            | `FINISHED`    |

## Regras das operações

| Operação       | Estado permitido | Alterações               |
| -------------- | ---------------- | ------------------------ |
| `create`       | nenhum           | cria `OPEN`              |
| `start_travel` | `OPEN`           | `start_travel`, `status` |
| `start_time`   | `ON_TRAVEL`      | `start_time`, `status`   |
| `finish`       | `ON_PROGRESS`    | `end_time`, `status`     |
| `update`       | qualquer         | altera dados do Ticket   |

Criação de Chamado informando Data e horário para atendimento, contratante, cliente final, valor, escopo
Botão de registro de inicio de deslocamento (registro de horario)
Botão de registro de chegada no local (registro de horario)
Botão de finalização do chamado que irá direcionar para um formulario para preenchimento dos dados restantes: protocolo, resumo técnico e horario de encerramento
