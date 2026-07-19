from dataclasses import dataclass
from copy import deepcopy

@dataclass(frozen=True)
class Checkpoint:
    name:str
    state:dict

class CheckpointManager:
    def __init__(self):
        self._points={}
    def create(self,name:str,state:dict)->Checkpoint:
        cp=Checkpoint(name=name,state=deepcopy(state))
        self._points[name]=cp
        return cp
    def restore(self,name:str)->dict:
        if name not in self._points:
            raise KeyError(name)
        return deepcopy(self._points[name].state)
