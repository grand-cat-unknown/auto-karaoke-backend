
from manim import *
import json
import re

class KaraokeScene(Scene):
    def construct(self):
        # Load lyrics
        with open('lyrics.txt') as f:
            lyrics = [line.strip().split() for line in f.readlines()]
        
        # remove emptylists from lyrics
        lyrics = [line for line in lyrics if line]

        # Load timestamps
        timestamp_json = json.load(open('timestamps.json'))
        timestamps = []
        song_length = timestamp_json['nonspeech_sections'][-1]['end']
        # Process timestamps
        for segment in timestamp_json['segments']:
            for word in segment['words']:
                start = word['start']
                end = word['end']
                # if next word doesn't start with a space, append it to the previous word
                if not word['word'].startswith(' '):
                    start = timestamps[-1][1]
                    timestamps[-1] = (start, end, timestamps[-1][2] + word['word'])
                else:
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
            print(line)
            print(one_line)
            synced_lyrics.append(one_line)

        # Display lyrics

        previous_end_time = 0  # Keep track of the end time of the last word
        for sentence in synced_lyrics:
            if not sentence:  # Skip empty sentences
                continue
            self.clear()
            line_group = VGroup()  # Group for the current line of lyrics

            for word_info in sentence:
                start, end, word_text = word_info
                word = Text(word_text, color=WHITE).scale(0.7)
                line_group.add(word)  # Add the word to the line group

            line_group.arrange(RIGHT, buff=0.1)  # Arrange words in a row
            self.add(line_group)  # Display the line

            pause_duration = sentence[0][0] - previous_end_time  # Calculate pause duration
            if pause_duration > 0:
                self.wait(pause_duration)  # Wait for the duration of the pause

            # Highlight words sequentially
            for i, word_info in enumerate(sentence):
                start, end, _ = word_info
                duration = end - start
                if duration <= 0:  # If duration is zero, highlight immediately
                    self.add(line_group[i].set_color(YELLOW))
                else:  # For non-zero durations, proceed with normal animation
                    self.play(line_group[i].animate.set_color(YELLOW), run_time=duration)
            
            previous_end_time = sentence[-1][1]
        # Wait for the remaining duration
        remaining_duration = song_length - previous_end_time
        if remaining_duration > 0:
            self.wait(remaining_duration)
