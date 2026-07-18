from enum import StrEnum

class ProjectType(StrEnum):
    EXISTING_HOSPITAL = "existing_hospital"
    GREENFIELD = "greenfield"

class AssetDisposition(StrEnum):
    RETAIN = "retain"
    UPGRADE = "upgrade"
    EXPAND = "expand"
    REPURPOSE = "repurpose"
    RETIRE = "retire"

class RoomType(StrEnum):
    RADIOPHARMACY = "radiopharmacy"
    CYCLOTRON = "cyclotron"
    INJECTION = "injection"
    UPTAKE = "uptake"
    PET_SCANNER = "pet_scanner"
    SPECT_SCANNER = "spect_scanner"
    WASTE = "waste"
    OTHER = "other"

class NodeType(StrEnum):
    RADIOPHARMACY = "radiopharmacy"
    CLINICAL_ROOM = "clinical_room"
    JUNCTION = "junction"
    VERTICAL_ENTRY = "vertical_entry"
    VERTICAL_EXIT = "vertical_exit"
    STATION = "station"

class RouteType(StrEnum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    EXTERNAL = "external"
    UNDERGROUND = "underground"

class ConstraintSense(StrEnum):
    MAXIMUM = "maximum"
    MINIMUM = "minimum"
    FIXED = "fixed"

class CarrierStatus(StrEnum):
    AVAILABLE = "available"
    IN_SERVICE = "in_service"
    CLEANING = "cleaning"
    MAINTENANCE = "maintenance"
    UNAVAILABLE = "unavailable"
