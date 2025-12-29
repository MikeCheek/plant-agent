from typing import Any, Optional
from smolagents.tools import Tool

class FinalAnswerTool(Tool):
    """
    A tool that provides a final answer to the given problem.
    Args:
        answer (`any`): The final answer to the problem
    Examples:
        ```python
        >>> final_answer("The plant needs watering every 3 days.")
        ```
    """
    name = "final_answer"
    description = "Provides a final answer to the given problem."
    inputs = {'answer': {'type': 'any', 'description': 'The final answer to the problem'}}
    output_type = "any"

    def forward(self, answer: Any) -> Any:
        return answer

    def __init__(self, *args, **kwargs):
        self.is_initialized = False
