from smolagents.tools import Tool
import datetime

class SeasonalContextTool(Tool):
    name = "seasonal_context"
    description = (
        "Provides the current date and the specific gardening season. "
        "Can adjust for Northern or Southern Hemispheres."
    )
    inputs = {
        "hemisphere": {
            "type": "string", 
            "description": "The hemisphere of the user: 'north' or 'south'. Defaults to 'north'.",
            "nullable": True
        }
    }
    output_type = "string"

    def forward(self, hemisphere: str = "north") -> str:
        now = datetime.datetime.now()
        month = now.month
        day = now.day
        
        # Determine base season (Northern Hemisphere)
        if month in [12, 1, 2]:
            season = "Winter"
        elif month in [3, 4, 5]:
            season = "Spring"
        elif month in [6, 7, 8]:
            season = "Summer"
        else:
            season = "Autumn/Fall"

        # Flip for Southern Hemisphere
        if hemisphere and hemisphere.lower() == "south":
            seasons_flip = {
                "Winter": "Summer",
                "Spring": "Autumn/Fall",
                "Summer": "Winter",
                "Autumn/Fall": "Spring"
            }
            season = seasons_flip[season]

        return (
            f"Today is {now.strftime('%B %d, %Y')}. "
            f"The current gardening season is {season} ({hemisphere.capitalize()} Hemisphere). "
            f"Daylight is {'increasing' if month < 6 else 'decreasing'} in the North."
        )