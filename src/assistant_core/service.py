from __future__ import annotations

import logging
import time

from assistant_core.config import Settings
from assistant_core.errors import InvalidRequest, ProviderError
from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.models import Intent, Message, Response, Source
from assistant_core.responder import TemplateResponder, make_responder
from assistant_core.router import route
from assistant_core.tools import parse_credits, tuition

log = logging.getLogger("assistant_core")


class AssistantService:
    def __init__(self, settings, offices, handbook, responder):
        self.settings = settings
        self.offices = offices
        self.handbook = handbook
        self.responder = responder
        self.fallback = TemplateResponder()

    def handle(self, msg: Message) -> Response:
        start_time = time.time()
        intent = route(msg.text, self.offices.names)

        try:
            if intent is Intent.GREETING:
                response = Response(answer="Hello! I can help with offices, fees and rules.", intent=intent)
            elif intent is Intent.FEE:
                response = self._fee(msg.text)
            elif intent is Intent.OFFICE:
                o = self.offices.find(msg.text)
                if o:
                    response = Response(answer=f"{o.name}: room {o.room}, open {o.hours}.", intent=intent)
                else:
                    response = Response(answer="Sorry, I don't know that office.", intent=Intent.UNKNOWN)
            else:
                response = self._rule(msg.text)
        finally:
            latency_ms = (time.time() - start_time) * 1000
            is_degraded = getattr(response, "degraded", False) if "response" in locals() else False
            intent_val = intent.value if hasattr(intent, "value") else str(intent)

            log.info(
                "handled",
                extra={
                    "intent": intent_val,
                    "latency_ms": round(latency_ms, 2),
                    "session": msg.session_id,
                    "degraded": is_degraded,
                },
            )

        return response

    def _fee(self, text: str) -> Response:
        try:
            credits, retake = parse_credits(text)
            total = tuition(
                credits,
                retake,
                self.settings.credit_rate_vnd,
                self.settings.retake_multiplier,
                self.settings.max_credits,
            )
            return Response(answer=f"Your tuition is {total} VND", intent=Intent.FEE)
        except InvalidRequest as e:
            return Response(answer=str(e), intent=Intent.FEE)

    def _rule(self, text: str) -> Response:
        rule = self.handbook.search(text)
        if rule is None:
            return Response(answer="Sorry I dont know", intent=Intent.UNKNOWN)

        sources = [Source(id=rule.id, title=rule.title)]
        try:
            answer = self.responder.explain(text, rule)
            return Response(answer=answer, intent=Intent.RULE, sources=sources)
        except ProviderError:
            log.warning("provider failed; using template fallback")
            answer = self.fallback.explain(text, rule)
            return Response(answer=answer, intent=Intent.RULE, sources=sources, degraded=True)

def build_service(settings: Settings) -> AssistantService:
    d = settings.data_dir
    offices = OfficeDirectory.from_csv(d / "offices.csv")
    handbook = Handbook.from_json(d / "handbook.json")
    return AssistantService(settings, offices, handbook, make_responder(settings.llm_provider))