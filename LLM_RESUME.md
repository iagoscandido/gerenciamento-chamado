# Projeto: Sistema de Gerenciamento de Chamados

## 1. Objetivo atual

O projeto começou como uma aplicação web em FastAPI + HTMX, mas o objetivo atual é adicionar um **bot do Telegram como interface principal**, reutilizando as mesmas regras de negócio.

Arquitetura desejada:

```text
Telegram
   ↓
Bot handlers
   ↓
TicketService
   ↓
SQLModel / Session
   ↓
SQLite
```

O princípio arquitetural é:

- handlers do Telegram cuidam da interação;
- `TicketService` cuida das regras de negócio;
- SQLModel cuida do modelo/persistência;
- não colocar regras de negócio dentro dos handlers;
- FastAPI pode permanecer no projeto como interface existente/teste, mas não deve concentrar regras.

O usuário prefere uma implementação simples, incremental e sem abstrações desnecessárias.

---

# 2. Preferências importantes do usuário

O usuário está aprendendo Python/FastAPI/SQLModel e prefere explicações claras sobre o motivo das alterações.

Regras importantes:

- Não assumir informações ausentes.
- Se faltar contexto necessário, pedir a informação.
- Implementar **uma etapa por vez**.
- Testar cada etapa antes de avançar.
- Não adicionar arquitetura desnecessária.
- Consultar documentação oficial antes de responder questões técnicas.
- Informar as fontes usadas para as afirmações técnicas.

Para este projeto, consultar preferencialmente:

- documentação oficial do Python;
- documentação oficial do Telegram Bot API;
- documentação oficial do `python-telegram-bot`;
- documentação oficial do FastAPI;
- documentação oficial do SQLModel;
- documentação oficial do Pydantic;
- documentação oficial do SQLAlchemy quando o comportamento vier dessa camada;
- documentação oficial do SQLite quando relevante.

Para Telegram, consultar **as duas camadas** quando necessário:

1. Telegram Bot API.
2. `python-telegram-bot`.

As respostas devem citar as fontes relevantes junto às afirmações.

O usuário quer que o desenvolvimento siga aproximadamente:

```text
documentação oficial
        ↓
implementação mínima
        ↓
teste
        ↓
próximo passo
```

---

# 3. Stack atual

- Python >= 3.13
- FastAPI
- SQLModel
- SQLite
- pytest
- `python-telegram-bot==22.8`
- `python-dotenv`

O ambiente usa `uv`.

Execução atual do bot:

```bash
uv run run_bot.py
```

Variável de ambiente:

```env
TELEGRAM_BOT_TOKEN=...
```

`.env` está no `.gitignore`.

---

# 4. Estrutura atual do projeto

Estrutura aproximada:

```text
gerenciamento-chamado/
├── database.db
├── database/
│   └── db.py
├── main.py
├── models/
│   └── ticket_model.py
├── routers/
│   └── ticket_router.py
├── services/
│   └── ticket_service.py
├── tests/
│   └── test_ticket_service.py
├── bot/
│   ├── __init__.py
│   └── handlers.py
├── run_bot.py
├── pyproject.toml
├── README.md
└── ...
```

Havia inicialmente um `bot.py` na raiz, mas isso causou conflito com o pacote `bot/`.

O arquivo foi renomeado para:

```text
run_bot.py
```

e foi criado:

```text
bot/__init__.py
```

Isso resolveu:

```text
ModuleNotFoundError: No module named 'bot.handlers'; 'bot' is not a package
```

---

# 5. Modelo de domínio atual

Arquivo:

```text
models/ticket_model.py
```

Modelo aproximadamente:

```python
from datetime import UTC, date, datetime, time
from enum import StrEnum

from sqlalchemy import Enum
from sqlmodel import Field, SQLModel


class TicketStatus(StrEnum):
    SCHEDULED = "scheduled"
    ON_TRAVEL = "on_travel"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    CANCELED = "canceled"


class Ticket(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    service_date: date
    service_time: time

    contractor: str
    client: str
    address: str

    scope: str
    value: float

    travel_start_time: time | None = None
    service_start_time: time | None = None
    service_finish_time: time | None = None

    technical_summary: str | None = None

    status: TicketStatus = Field(
        default=TicketStatus.SCHEDULED,
        sa_type=Enum(
            TicketStatus,
            values_callable=lambda enum: [item.value for item in enum],
        ),
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    updated_at: datetime | None = None


class TicketCreate(SQLModel):
    service_date: date
    service_time: time
    contractor: str
    client: str
    address: str
    scope: str
    value: float
```

Decisões importantes:

- `service_date` e `service_time` representam o **agendamento do atendimento**, não o momento em que o ticket foi criado.
- O atendimento pode ser agendado para uma data futura.
- `created_at` representa quando o ticket foi criado.
- `created_at` usa UTC.
- `travel_start_time`, `service_start_time` e `service_finish_time` ainda são apenas `time`, não `datetime`. Isso foi mantido conscientemente por enquanto.
- `contractor` e `client` são strings. Não criar tabelas separadas sem necessidade concreta.
- Status persistido pelo valor do enum, por exemplo `scheduled`, e não pelo nome `SCHEDULED`.

---

# 6. Banco

Arquivo:

```text
database/db.py
```

Estrutura aproximada:

```python
from sqlmodel import Session, SQLModel, create_engine

from models.ticket_model import Ticket

DATABASE_URL = "sqlite:///tickets.db"

engine = create_engine(
    DATABASE_URL,
    echo=True,
)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
```

`get_session()` é usado como dependência do FastAPI.

Não assumir que ele pode ser utilizado como:

```python
with get_session():
```

Ele é um generator/dependency.

---

# 7. TicketService

Arquivo:

```text
services/ticket_service.py
```

Implementação atual:

```python
from datetime import UTC, datetime

from sqlmodel import Session

from models.ticket_model import Ticket, TicketCreate, TicketStatus


class TicketService:
    def __init__(self, session: Session):
        self.session = session

    def start_travel(self, ticket_id: int) -> Ticket:
        ticket = self._get_ticket(ticket_id)

        if ticket.status != TicketStatus.SCHEDULED:
            raise ValueError(
                "Ticket cannot start travel from its current status"
            )

        now = datetime.now(UTC)

        ticket.travel_start_time = now.time()
        ticket.status = TicketStatus.ON_TRAVEL
        ticket.updated_at = now

        self.session.commit()
        self.session.refresh(ticket)

        return ticket

    def cancel(self, ticket_id: int) -> Ticket:
        ticket = self._get_ticket(ticket_id)

        if ticket.status not in {
            TicketStatus.SCHEDULED,
            TicketStatus.ON_TRAVEL,
        }:
            raise ValueError(
                "Ticket cannot be canceled from its current status"
            )

        now = datetime.now(UTC)

        ticket.status = TicketStatus.CANCELED
        ticket.updated_at = now

        self.session.commit()
        self.session.refresh(ticket)

        return ticket

    def start_service(self, ticket_id: int) -> Ticket:
        ticket = self._get_ticket(ticket_id)

        if ticket.status != TicketStatus.ON_TRAVEL:
            raise ValueError("Ticket cannot start service")

        now = datetime.now(UTC)

        ticket.service_start_time = now.time()
        ticket.status = TicketStatus.IN_PROGRESS
        ticket.updated_at = now

        self.session.commit()
        self.session.refresh(ticket)

        return ticket

    def finish_service(self, ticket_id: int) -> Ticket:
        ticket = self._get_ticket(ticket_id)

        if ticket.status != TicketStatus.IN_PROGRESS:
            raise ValueError("Ticket cannot finish service")

        now = datetime.now(UTC)

        ticket.service_finish_time = now.time()
        ticket.status = TicketStatus.FINISHED
        ticket.updated_at = now

        self.session.commit()
        self.session.refresh(ticket)

        return ticket

    def create(self, ticket: TicketCreate) -> Ticket:
        db_ticket = Ticket.model_validate(ticket)

        self.session.add(db_ticket)
        self.session.commit()
        self.session.refresh(db_ticket)

        return db_ticket

    def _get_ticket(self, ticket_id: int) -> Ticket:
        ticket = self.session.get(Ticket, ticket_id)

        if ticket is None:
            raise ValueError("Ticket not found")

        return ticket
```

Importante:

`create()` recebe:

```python
TicketCreate
```

e cria internamente:

```python
Ticket.model_validate(ticket)
```

retornando um `Ticket` persistido.

Isso foi ajustado depois de um teste que falhou porque `TicketCreate` não possui `id`.

---

# 8. Máquina de estados

As regras definidas pelo usuário são:

| Estado atual  | Iniciar viagem | Iniciar atendimento | Finalizar | Cancelar |
| ------------- | -------------: | ------------------: | --------: | -------: |
| `SCHEDULED`   |            sim |                 não |       não |      sim |
| `ON_TRAVEL`   |            não |                 sim |       não |      sim |
| `IN_PROGRESS` |            não |                 não |       sim |      não |
| `FINISHED`    |            não |                 não |       não |      não |
| `CANCELED`    |            não |                 não |       não |      não |

Cancelamento:

- permitido depois da criação;
- permitido em `SCHEDULED`;
- permitido em `ON_TRAVEL`;
- proibido quando o atendimento começou;
- `CANCELED` é terminal.

O usuário explicitamente preferiu não criar uma arquitetura excessivamente defensiva. Não adicionar state machine genérica, repositories, hierarquia de exceções, auth etc. sem necessidade.

---

# 9. Testes

Existem atualmente **12 testes passando** no serviço.

Último resultado confirmado:

```text
12 passed
```

Testes:

```text
1. test_start_travel
2. test_start_travel_when_already_on_travel
3. test_cancel_scheduled_ticket
4. test_cancel_ticket_on_travel
5. test_cannot_cancel_ticket_in_progress
6. test_cannot_cancel_finished_ticket
7. test_cannot_cancel_canceled_ticket
8. test_start_service
9. test_start_service_when_scheduled
10. test_finish_service
11. test_finish_service_when_scheduled
12. test_create_ticket
```

O usuário prefere manter a estrutura atual dos testes por enquanto, sem refatorar fixtures desnecessariamente.

---

# 10. Bot Telegram

Biblioteca:

```text
python-telegram-bot==22.8
```

O bot básico `/start` já funcionou.

Mensagem:

```text
Sistema de Chamados
```

O runner é:

```text
run_bot.py
```

A lógica de conversa está:

```text
bot/handlers.py
```

---

# 11. ConversationHandler atual

O fluxo desejado para criação é:

```text
/novo
  ↓
data do atendimento
  ↓
horário
  ↓
contratante
  ↓
cliente
  ↓
endereço
  ↓
serviço
  ↓
valor
  ↓
resumo
  ↓
confirmação
  ↓
TicketService.create()
  ↓
SCHEDULED
```

O usuário quer confirmação antes de persistir.

---

# 12. Código atual de `bot/handlers.py`

O usuário mostrou esta versão:

```python
from telegram.ext import ConversationHandler

from datetime import datetime

from telegram import Update

from telegram.ext import ContextTypes


SERVICE_DATE = 0
SERVICE_TIME = 1
CONTRACTOR = 2
CLIENT = 3


async def start_ticket(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    print("DEBUG: start_ticket foi chamado")
    print(f"DEBUG: mensagem = {update.message.text}")

    await update.message.reply_text(
        "Informe a data do atendimento no formato DD/MM/AAAA:"
    )

    print(f"DEBUG: retornando estado {SERVICE_DATE}")

    return SERVICE_DATE


async def receive_service_date(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    print("DEBUG: receive_service_date foi chamado")
    print(f"DEBUG: mensagem = {update.message.text}")

    text = update.message.text.strip()

    try:
        service_date = datetime.strptime(
            text,
            "%d/%m/%Y",
        ).date()

        print(f"DEBUG: data convertida = {service_date}")

    except ValueError:
        print("DEBUG: data inválida")

        await update.message.reply_text(
            "Data inválida. Informe no formato DD/MM/AAAA:"
        )

        return SERVICE_DATE

    context.user_data["service_date"] = service_date

    print(
        "DEBUG: service_date armazenada =",
        context.user_data["service_date"],
    )

    await update.message.reply_text(
        "Informe o horário do atendimento no formato HH:MM:"
    )

    print(f"DEBUG: retornando estado {SERVICE_TIME}")

    return SERVICE_TIME


async def receive_service_time(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    print("DEBUG: receive_service_time foi chamado")
    print(f"DEBUG: mensagem = {update.message.text}")

    text = update.message.text.strip()

    try:
        service_time = datetime.strptime(
            text,
            "%H:%M",
        ).time()

        print(f"DEBUG: horário convertido = {service_time}")

    except ValueError:
        print("DEBUG: horário inválido")

        await update.message.reply_text(
            "Horário inválido. Informe no formato HH:MM:"
        )

        return SERVICE_TIME

    context.user_data["service_time"] = service_time

    print(
        "DEBUG: service_time armazenado =",
        context.user_data["service_time"],
    )

    await update.message.reply_text(
        "Informe o contratante:"
    )

    print(f"DEBUG: retornando estado {CONTRACTOR}")

    return CONTRACTOR


async def receive_contractor(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    contractor = update.message.text.strip()

    context.user_data["contractor"] = contractor

    await update.message.reply_text(
        "Contratante registrado."
    )

    return CLIENT


async def receive_client(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    client = update.message.text.strip()

    context.user_data["client"] = client

    await update.message.reply_text(
        "Cliente registrado."
    )

    return ConversationHandler.END
```

IMPORTANTE: foi corrigido um erro anterior em `receive_service_time()`.

Antes estava:

```python
return ConversationHandler.END
```

mesmo depois de pedir o contratante.

O correto agora é:

```python
return CONTRACTOR
```

Isso permite a transição:

```text
SERVICE_TIME → CONTRACTOR
```

---

# 13. Estado atual confirmado

O usuário confirmou que o fluxo até o cliente está funcionando.

Fluxo validado:

```text
/novo
  ↓
25/09/2026
  ↓
14:30
  ↓
Empresa XPTO
  ↓
João da Silva
  ↓
Cliente registrado.
```

Também foram adicionados `print()` de debug porque inicialmente a conversa não avançava corretamente.

O usuário confirmou:

> funcional

Portanto, não reimplementar essas etapas sem necessidade.

---

# 14. `run_bot.py`

O runner deve conter um `ConversationHandler` aproximadamente assim:

```python
ticket_conversation = ConversationHandler(
    entry_points=[
        CommandHandler("novo", start_ticket),
    ],
    states={
        SERVICE_DATE: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                receive_service_date,
            ),
        ],
        SERVICE_TIME: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                receive_service_time,
            ),
        ],
        CONTRACTOR: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                receive_contractor,
            ),
        ],
        CLIENT: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                receive_client,
            ),
        ],
    },
    fallbacks=[],
)
```

E:

```python
application.add_handler(CommandHandler("start", start))
application.add_handler(ticket_conversation)

application.run_polling()
```

---

# 15. Como continuar

O próximo campo planejado é:

```text
CLIENT
  ↓
ADDRESS
```

Ou seja, coletar o endereço do atendimento.

Ainda NÃO:

- criar o Ticket;
- chamar `TicketService.create()`;
- gravar no banco;
- implementar confirmação;
- implementar valor;
- implementar escopo.

A abordagem desejada é continuar uma etapa por vez.

Próximo passo recomendado:

1. consultar documentação oficial do Telegram Bot API;
2. consultar documentação oficial do `python-telegram-bot 22.8`;
3. adicionar `ADDRESS = 4`;
4. fazer `receive_client()` retornar `ADDRESS`;
5. criar `receive_address()`;
6. armazenar em `context.user_data["address"]`;
7. temporariamente encerrar a conversa;
8. testar;
9. somente depois avançar para o próximo campo.

Não alterar a arquitetura do `TicketService` neste momento.

---

# 16. Fontes oficiais que devem ser consultadas

Telegram:

- Telegram Bot API:
  https://core.telegram.org/bots/api

- Telegram Bots:
  https://core.telegram.org/bots

python-telegram-bot:

- Documentação:
  https://docs.python-telegram-bot.org/en/latest/

- ConversationHandler:
  https://docs.python-telegram-bot.org/en/latest/telegram.ext.conversationhandler.html

- ContextTypes / user_data:
  https://docs.python-telegram-bot.org/en/latest/telegram.ext.contexttypes.html

- Filters:
  https://docs.python-telegram-bot.org/en/latest/telegram.ext.filters.html

Python:

- datetime:
  https://docs.python.org/3/library/datetime.html

FastAPI:

- https://fastapi.tiangolo.com/

SQLModel:

- https://sqlmodel.tiangolo.com/

Pydantic:

- https://docs.pydantic.dev/

SQLite:

- https://sqlite.org/docs.html

Sempre citar as fontes utilizadas para as afirmações técnicas.

---

# 17. Problemas anteriores relevantes

## Erro de importação

Existia:

```text
bot.py
bot/
    handlers.py
```

Isso gerava:

```text
ModuleNotFoundError:
No module named 'bot.handlers'; 'bot' is not a package
```

Resolvido renomeando:

```text
bot.py → run_bot.py
```

e criando:

```text
bot/__init__.py
```

## Erro de callback

O `ConversationHandler` passou dois argumentos:

```python
start_ticket(update, context)
```

mas a função inicialmente aceitava apenas:

```python
start_ticket(update)
```

Resultado:

```text
TypeError:
start_ticket() takes 1 positional argument but 2 were given
```

Corrigido para:

```python
async def start_ticket(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
```

## Problema de transição

`receive_service_time()` estava retornando:

```python
ConversationHandler.END
```

depois de pedir o contratante.

Corrigido para:

```python
return CONTRACTOR
```

---

# 18. Filosofia de implementação

O usuário quer evitar “overengineering”.

Não introduzir:

- repository pattern;
- service abstractions adicionais;
- generic state machines;
- DTOs extras;
- classes de handlers desnecessárias;
- autenticação;
- sistema de auditoria;
- tratamento excessivamente defensivo;
- tabelas para contractor/client sem necessidade.

O projeto é inicialmente para uso pessoal, portanto a prioridade é:

```text
clareza
+
simplicidade
+
funcionalidade
+
testes incrementais
```
