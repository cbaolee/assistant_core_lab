import sys
from pathlib import Path
from assistant_core.config import load_settings
from assistant_core.knowledge import OfficeDirectory, Handbook
from assistant_core.responder import StubLLMResponder
from assistant_core.service import AssistantService
from assistant_core.models import Message
from assistant_core.logging_setup import setup_logging

def main():
    settings = load_settings()
    setup_logging(settings.log_level)
    
    offices_path = settings.data_dir / "offices.csv"
    handbook_path = settings.data_dir / "handbook.json"
    
    offices = OfficeDirectory.from_csv(offices_path)
    handbook = Handbook.from_json(handbook_path)
    
    responder = StubLLMResponder(fail=False)
    service = AssistantService(settings, offices, handbook, responder)

    if len(sys.argv) > 1:
        msg_text = " ".join(sys.argv[1:])
        msg = Message(text=msg_text)
        response = service.handle(msg)
        print(response.answer)
    else:
        print("Assistant ready. Type 'quit' to exit.")
        while True:
            try:
                q = input("> ")
                if q.lower() == "quit":
                    break
                if not q.strip():
                    continue
                msg = Message(text=q)
                response = service.handle(msg)
                print(response.answer)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    main()