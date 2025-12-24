
# src/humanize.py

import random
from typing import Union, Callable
from .note import Note
from .chord import Chord
from .arpeggiator import Arpeggiator
from .drums import DrumPattern
from .sequencer import Sequencer

# Type alias for anything that can be humanized
Humanizable = Union[Note, Chord, Arpeggiator, DrumPattern, Sequencer]


def humanize(
    obj: Humanizable,
    time: float = 0.02,
    velocity: int = 12,
    tuning: float = 0.0,
    seed: int | None = None,
) -> Humanizable:
    """
    Add human feel to a playable object by introducing small random variations.

    Args:
        obj: The object to humanize (Note, Chord, Arpeggiator, DrumPattern, Sequencer, etc.)
        time: Max timing offset in seconds (+/-) — e.g., 0.02 = up to 20ms early/late
        velocity: Max velocity variation (+/-) — e.g., 12 = notes vary by up to 12 velocity points
        tuning: Max pitch detune in cents (+/-) — e.g., 10.0 for subtle warmth
        seed: Optional random seed for reproducible "human" performances

    Returns:
        The same object (for chaining), now with humanization applied

    Examples:
        Chord("Cmaj7").velocity(90).humanize(time=0.03, velocity=15).play()

        DrumPattern.basic_rock().humanize(time=0.015, velocity=8).play(loop=4)
    """
    if seed is not None:
        random.seed(seed)

    # Store humanization parameters on the object
    if not hasattr(obj, "_humanize_params"):
        obj._humanize_params = {}

    obj._humanize_params.update(
        {
            "time_offset": time,
            "velocity_range": velocity,
            "tuning_cents": tuning,
        }
    )

    # Monkey-patch or wrap .play() if not already done
    if not hasattr(obj, "_original_play"):
        obj._original_play = obj.play

        def make_humanized_play(original_play: Callable) -> Callable:
            def humanized_play(*args, **kwargs):
                params = getattr(obj, "_humanize_params", {})

                time_offset = params.get("time_offset", 0.0)
                vel_range = params.get("velocity_range", 0)
                tuning_cents = params.get("tuning_cents", 0.0)

                # Apply global time offset before playing
                if time_offset > 0:
                    offset = random.uniform(-time_offset, time_offset)
                    # Positive offset = delay, negative = play early
                    if offset > 0:
                        import time
                        time.sleep(offset)

                # Now play — individual notes will get per-note variation
                # We inject humanization via context if the object supports it
                if hasattr(obj, "play_with_humanization"):
                    obj.play_with_humanization(
                        original_play,
                        vel_range=vel_range,
                        tuning_cents=tuning_cents,
                        *args,
                        **kwargs
                    )
                else:
                    original_play(*args, **kwargs)

            return humanized_play

        obj.play = make_humanized_play(obj._original_play)

    return obj


# Optional: Add .humanize() method directly to your classes via monkey patch or inheritance
# You can import this in __init__.py and apply:

def add_humanize_method():
    """Call this in your package __init__ to add .humanize() to main classes"""
    for cls in (Note, Chord, Arpeggiator, DrumPattern, Sequencer):
        if not hasattr(cls, "humanize"):
            cls.humanize = lambda self, time=0.02, velocity=12, tuning=0.0, seed=None: humanize(
                self, time=time, velocity=velocity, tuning=tuning, seed=seed
            )