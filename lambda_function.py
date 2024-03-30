import json
import random
import os
from pathlib import Path
import re
from dotenv import load_dotenv
from pytube import YouTube
from lyrics_extractor import SongLyrics
import boto3
import requests

load_dotenv()

s3 = boto3.client('s3', aws_access_key_id=os.environ.get('AWS_S3_ACCESS_ID'), aws_secret_access_key=os.environ.get('AWS_S3_ACCESS_KEY'))

class RunPodServerlessEndpointSync:
    def __init__(self, endpoint_url):
        self.api_key = os.getenv("RUNPOD_API")
        self.url = f"https://api.runpod.ai/v2/{endpoint_url}/runsync"

    def run(self, payload):
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": self.api_key
        }
        response = requests.post(self.url, json=payload, headers=headers)
        return response

class RunPodServerlessEndpointASync:
    def __init__(self, endpoint_url):
        self.api_key = os.getenv("RUNPOD_API")
        self.url = f"https://api.runpod.ai/v2/{endpoint_url}/run"

    def run(self, payload):
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": self.api_key
        }
        response = requests.post(self.url, json=payload, headers=headers)
        return response

def clean_lyrics(lyrics):
    # remove everything in between [ and ] using regex
    lyrics = re.sub(r"\[.*?\]", "", lyrics)
    return lyrics



def youtube2mp3 (url,outdir):

    yt = YouTube(url)
    video = yt.streams.filter(only_audio=True).first()
    out_file = video.download(output_path=outdir)
    base, ext = os.path.splitext(out_file)
    new_file = Path(f'{outdir}/base_song.mp3')
    os.rename(out_file, new_file)

    if new_file.exists():
        print(f'{yt.title} has been successfully downloaded.')
    else:
        print(f'ERROR: {yt.title} could not be downloaded!')
    
    song_name = yt.title
    s3.upload_file(f'{outdir}/base_song.mp3', 'auto-karaoke', f'{song_name}/base_song.mp3')

    return song_name

def lyrics_extractor(song_name,outdir):
    print(f"Extracting lyrics for {song_name}")
    extract_lyrics = SongLyrics(os.environ.get('GCS_API_KEY'), os.environ.get('GCS_ENGINE_ID'))
    data = extract_lyrics.get_lyrics(song_name)
    data = data['lyrics']
    data = clean_lyrics(data)
    print(data)
    with open(f'{outdir}/lyrics.txt', 'w') as f:
        f.write(data)
    s3.upload_file(f'{outdir}/lyrics.txt', 'auto-karaoke', f'{song_name}/lyrics.txt')
    return data

def lambda_handler(event, context):
    output_dir = "/tmp"
    from youtubesearchpython import VideosSearch

    videosSearch = VideosSearch(event['body']['song_name'] + " song audio", limit = 2)

    print(videosSearch.result())
    url = videosSearch.result()['result'][0]["link"]

    print("Converting to mp3")
    song_name = youtube2mp3(url,output_dir)

    # print("Extracting lyrics")
    real_lyrics = lyrics_extractor(song_name, output_dir)
    
    print("SONG NAME: ", song_name)
    
    payload = {
        "input": {
            "song_name": song_name,
        }
    }

    print("Splitting audio")
    spleeter_endpoint = RunPodServerlessEndpointSync(os.environ.get("SPLEETER_ENDPOINT_ID"))
    spleeter_response = spleeter_endpoint.run(payload)
    print(spleeter_response)

    print("Vocals to text")
    whisper_endpoint = RunPodServerlessEndpointASync(os.environ.get("WHISPER_ENDPOINT_ID"))
    whipser_response = whisper_endpoint.run(payload)
    # {
    #     "delayTime": 67838,
    #     "executionTime": 16003,
    #     "id": "2e2e1d8b-61cf-4096-bf9a-56d57ca17194-e1",
    #     "output": "DONE!",
    #     "status": "COMPLETED"
    # }
    # print(whipser_response["id"],spleeter_response["id"])
    # s3.download_file('auto-karaoke', f'{song_name}/timestamps.json', 'timestamps.json')

    return whipser_response

# if __name__ == "__main__":
#     # load test.json
#     with open('test.json') as f:
#         json_file = json.load(f)
#     lambda_handler(json_file, None)

