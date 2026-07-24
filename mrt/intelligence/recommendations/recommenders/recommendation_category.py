from enum import Enum

class RecommendationCategory(str, Enum):
    THROUGHPUT = "throughput"
    EQUIPMENT = "equipment"
    STAFFING = "staffing"
    TRANSPORT = "transport"
    RADIATION = "radiation"
    ECONOMICS = "economics"
    GENERAL = "general"
