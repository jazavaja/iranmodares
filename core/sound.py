"""
Sound utilities for notifications.
"""

import pygame

from config import ALARM_SOUND


def play_alarm():
    """Play alarm sound."""
    try:
        pygame.mixer.init()
        sound = pygame.mixer.Sound(ALARM_SOUND)
        sound.play()
        pygame.time.delay(int(sound.get_length() * 1000))
    except Exception as e:
        print(f"⚠️ Could not play sound: {e}")