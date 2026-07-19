from dataclasses import dataclass

@dataclass(frozen=True)
class DeadlockRecoveryPlan:
    victim:str
    reason:str="lowest recovery cost"

def select_deadlock_victim(participants:list[str])->DeadlockRecoveryPlan:
    if not participants:
        raise ValueError("participants required")
    return DeadlockRecoveryPlan(victim=sorted(participants)[0])
