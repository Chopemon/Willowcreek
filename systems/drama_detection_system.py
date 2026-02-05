# systems/drama_detection_system.py
# Dramatic scene detection and narrative description.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from services.scene_image_generator import ImagePromptGenerator, SceneContext


@dataclass
class DramaticScene:
    title: str
    location: str
    participants: List[str]
    description: str
    generate_image: bool = False
    image_prompt: Optional[str] = None


class DramaDetectionSystem:
    """
    Detect dramatic scenes based on event text.
    """

    def __init__(self):
        self.scenes: List[DramaticScene] = []
        self.prompt_generator = ImagePromptGenerator()

    def evaluate_events(self, events: List[dict]) -> List[DramaticScene]:
        new_scenes: List[DramaticScene] = []
        for event in events:
            label = event.get("type", "")
            if label in {"conflict", "breakup", "death", "confession"}:
                scene = DramaticScene(
                    title=f"Dramatic {label.title()}",
                    location=event.get("location", "Unknown"),
                    participants=event.get("participants", []),
                    description=event.get("summary", "A dramatic moment unfolded."),
                    generate_image=True,
                )
                context = SceneContext(
                    scene_type="drama",
                    priority=7,
                    characters=scene.participants,
                    location=scene.location,
                    time_of_day=event.get("time_of_day", "evening"),
                    weather=event.get("weather", "clear"),
                    mood="tense",
                    explicit_level=0,
                    activity=scene.description,
                    raw_event=scene.description,
                )
                scene.image_prompt = self.prompt_generator.generate_prompt(context)[0]
                new_scenes.append(scene)
                self.scenes.append(scene)
        return new_scenes
