import subprocess
import requests
import shlex

req = requests.get('http://localhost:5005/video-inference')
b = req.json()

for i in range(len(b['inferences'][0]['clock_segments'])):
    command = f"ffmpeg -i '{b['inferences'][0]['filename']}' -ss {b['inferences'][0]['clock_segments'][i]['start']} -t  {b['inferences'][0]['clock_segments'][i]['length']} -c copy {i}.mp4"
    subprocess.call(shlex.split(command))
