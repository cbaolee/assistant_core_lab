# Architecture Note: Assistant Core

## 1. Module Responsibilities
| Module | Responsibility |
| :--- | :--- |
| `config.py` | read settings from the environment; validate |
| `errors.py` | named exceptions |
| `models.py` | public contract: Message, Response, Intent, Source |
| `router.py` | choose an Intent with simple rules |
| `knowledge.py` | office directory (CSV) and handbook (JSON) with search |
| `tools.py` | deterministic tuition calculation |
| `responder.py` | response generation behind one interface (stub LLM, template) |
| `service.py` | `AssistantService.handle(Message) -> Response` (the only entry point) |
| `logging_setup.py` | structured JSON logs |
| `__main__.py` | command-line interface |

## 2. Service Interface
The CLI, the FastAPI backend (Lab 4), and the UI (Lab 7) all call this one method:
`AssistantService.handle(msg: Message) -> Response`

*   **Message:** text (1-2000 chars), session_id
*   **Response:** answer, intent, sources [], degraded (True if a fallback was used)
*   **Errors:** invalid input -> `ValidationError`; startup -> `ConfigError` / `DataError`; provider failures never reach the caller (fallback instead).

## 3. Design Decisions
1.  **Pure Functions for Tools:** Fees are computed in `tools.py`, never by an LLM, making them exact and testable.
2.  **Adapter Pattern for AI:** The LLM sits behind the `Responder` interface; the stub needs no key, so tests and CI run offline.
3.  **Environment-based Configuration:** Configuration comes from the environment, and `.env.example` documents every variable (following Twelve-Factor App principles).