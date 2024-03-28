from manim import *
import json
import re

class KaraokeScene(Scene):
    def construct(self):
        # Load lyrics
        with open('lyrics.txt') as f:
            lyrics = [line.strip().split() for line in f.readlines()]

        # Load timestamps
        timestamp_json = json.load(open('timestamps.json'))
        timestamps = []

        # Process timestamps
        for segment in timestamp_json['segments']:
            for word in segment['words']:
                start = word['start']
                end = word['end']
                word_text = re.sub(r"\s+", "", word['word'])  # Clean word text
                timestamps.append((start, end, word_text))

        # Sync lyrics with timestamps
        i = 0
        synced_lyrics = []
        for line in lyrics:
            one_line = []
            for word in line:
                if i >= len(timestamps):
                    break
                start, end, text = timestamps[i]
                one_line.append((start, end, text))
                i += 1
            synced_lyrics.append(one_line)

        for sentence in synced_lyrics[:3]:
            self.clear()

            line_group = VGroup()  # Group for the current line of lyrics
            for word_info in sentence:
                start, end, word_text = word_info
                word = Text(word_text, color=WHITE).scale(0.7)
                line_group.add(word)  # Add the word to the line group
            
            line_group.arrange(RIGHT, buff=0.1)  # Arrange words in a row
            self.add(line_group)  # Display the line
            
            # Highlight words sequentially
            for i, word_info in enumerate(sentence):
                start, end, _ = word_info
                duration = end - start
                if duration <= 0:  # If duration is zero, highlight immediately
                    self.add(line_group[i].set_color(YELLOW))
                else:  # For non-zero durations, proceed with normal animation
                    self.play(line_group[i].animate.set_color(YELLOW), run_time=duration)
