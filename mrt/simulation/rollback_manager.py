from dataclasses import dataclass

@dataclass(frozen=True)
class RollbackAction:
    resource_name:str
    reason:str

class RollbackManager:
    def rollback(self, allocations:list[str])->list[RollbackAction]:
        return [RollbackAction(a,"deadlock recovery") for a in allocations]
