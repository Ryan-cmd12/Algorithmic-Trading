from abc import ABC, abstractmethod

class ExecutionHandler(ABC):
    @abstractmethod
    def execute_order(self,event):
        raise NotImplementedError('please implement execute_order()')
    
class SimulatedExecutionHander(ExecutionHandler):
    def __init__(self,events):
        self.events = events
    def execute_order(self, event):
        if event.type == 'ORDER':
            