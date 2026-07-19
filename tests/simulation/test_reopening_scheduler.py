from datetime import datetime
from mrt.simulation.reopening_scheduler import ReopeningEvent

def test_event_creation():
    event=ReopeningEvent("PET", datetime(2026,7,20,8,0))
    assert event.resource_name=="PET"
