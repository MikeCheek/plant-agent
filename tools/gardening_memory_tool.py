from smolagents.tools import Tool
import os
import json

class GardenMemoryTool(Tool):
    """
      A tool that maintains persistent memory of the user's garden. Use 'save' to update specific keys
      (location, hardiness_zone, plants) and 'retrieve' to see all stored data.
      Args:
          action (`str`): The action to perform: 'save' to add/update info, or 'retrieve' to read it.
          key (`str`, optional): The specific category (e.g., 'location', 'plants', 'zone'). Required for 'save'.
          value (`any`, optional): The information to store. Can be a string, list, or number. Required for 'save'.
      Examples:
          ```python
          >>> garden_memory("save", key="location", value="San Francisco, CA")
          >>> garden_memory("retrieve")
          ```
    """
    name = "garden_memory"
    description = (
        "Maintains persistent memory of the user's garden. Use 'save' to update specific keys "
        "(location, hardiness_zone, plants) and 'retrieve' to see all stored data."
    )
    inputs = {
        "action": {
            "type": "string", 
            "description": "The action to perform: 'save' to add/update info, or 'retrieve' to read it."
        },
        "key": {
            "type": "string", 
            "description": "The specific category (e.g., 'location', 'plants', 'zone'). Required for 'save'.",
            "nullable": True
        },
        "value": {
            "type": "any", 
            "description": "The information to store. Can be a string, list, or number. Required for 'save'.",
            "nullable": True
        }
    }
    output_type = "string"

    def __init__(self, *args, **kwargs):
        self.memory_file = "garden_memory.json"
        super().__init__(*args, **kwargs)

    def _load_memory(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def forward(self, action: str, key: str = None, value: any = None) -> str:
        memory = self._load_memory()

        if action == "save":
            if not key or value is None:
                return "Error: Both 'key' and 'value' are required when saving information."
            
            # Update specific key without losing others
            memory[key] = value
            with open(self.memory_file, "w") as f:
                json.dump(memory, f, indent=4)
            return f"Successfully updated '{key}' in garden memory."

        elif action == "retrieve":
              if not memory:
                  return "The garden memory is currently empty. I don't have any locations or plants saved yet."
              
              # Create a clean, human-readable summary
              lines = ["Here is what I remember about the garden:"]
              for key, value in memory.items():
                  # Clean up the key name (e.g., 'hardiness_zone' -> 'Hardiness Zone')
                  clean_key = key.replace('_', ' ').title()
                  
                  # Format the value: if it's a list, join it with commas; otherwise, use it as is
                  if isinstance(value, list):
                      clean_value = ", ".join(value)
                  else:
                      clean_value = value
                  
                  lines.append(f"- {clean_key}: {clean_value}")
                  
              return "\n".join(lines)

        return "Invalid action. Use 'save' or 'retrieve'."