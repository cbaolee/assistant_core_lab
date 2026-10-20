from assistant_core.router import route
from assistant_core.models import Intent

def test_route_greeting():
    assert route("hello", set()) == Intent.GREETING

def test_route_fee():
    assert route("how much is the tuition", set()) == Intent.FEE

def test_route_office():
    assert route("where is the library", {"library", "a101"}) == Intent.OFFICE

def test_route_rule():
    assert route("how to register for a thesis", set()) == Intent.RULE