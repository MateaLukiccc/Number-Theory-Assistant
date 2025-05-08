from typing import Dict, Any

class Agent:
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement the run method.")