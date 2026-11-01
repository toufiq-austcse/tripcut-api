"""YAMNet (AudioSet) class names grouped into the audio events we score."""

AUDIO_EVENT_GROUPS = {
    "laughter": ("Laughter", "Giggle", "Chuckle, chortle", "Belly laugh", "Baby laughter", "Snicker"),
    "cheer": ("Cheering", "Applause", "Crowd", "Children shouting", "Yell"),
    "music": ("Music", "Singing"),
    "wind": ("Wind", "Wind noise (microphone)", "Rustling leaves"),
    "speech": ("Speech", "Conversation"),
}
AUDIO_SCORE_THRESHOLD = 0.05
