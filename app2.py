import os.path
import shutil
import hashlib
import uuid
from urllib.request import urlopen, Request

def download_file(url, timeout=10):
    block_size = 1000 * 1000
    tmp_file_path = "./download/" + str(uuid.uuid4()) + ".part"

    first_byte = 0
    file_size = -1
    try:
        file_size = int(urlopen(url).info().get("Content-Length", -1))

        while first_byte < file_size:
            last_byte = first_byte + block_size if first_byte + block_size < file_size else file_size - 1
            
            req = Request(url)
            req.headers['Range'] = "bytes=%s-%s" % (first_byte, last_byte)
            data_chunk = urlopen(req, timeout=timeout).read()
            
            with open(tmp_file_path, "ab") as f:
                f.write(data_chunk)

            first_byte = last_byte + 1
    except IOError as e:
        print("IO Error - %s" % e)
    finally:
        if file_size == os.path.getsize(tmp_file_path):
            m = hashlib.md5()
            with open(tmp_file_path, "rb") as f:
                while True:
                    chunk = f.read(1000 * 1000)  # 1MB
                    if not chunk:
                        break
                    m.update(chunk)
            hash = m.hexdigest()

            file_path = "./download/" + hash
            if(os.path.exists(file_path)):
                os.remove(tmp_file_path)
            else:
                shutil.move(tmp_file_path, file_path)
            return { "path": file_path, "hash": hash }
    return None

import assemblyai as aai

aai.settings.api_key = "4681af9219474205ad82e1b8a27e549a"
config = aai.TranscriptionConfig(speaker_labels=True, language_code="pt")
transcriber = aai.Transcriber()

#FILE_URL = "https://storage.googleapis.com/aai-web-samples/news.mp4"
#FILE_URL = "https://github.com/AssemblyAI-Examples/audio-examples/raw/main/20230607_me_canadian_wildfires.mp3"
FILE_URL = "./pvc-fm.m4a"
#downloaded_file = download_file(FILE_URL)

transcript = transcriber.transcribe(FILE_URL, config=config)

print(transcript.text)

utterances = []
for utterance in transcript.utterances:
    utterances.append([utterance.speaker, utterance.start, utterance.end])
    print(f"Speaker {utterance.speaker}: {utterance.text}")

print(utterances)

import functools

#data = [['A', 250, 26950], ['B', 27850, 28920], ['A', 29290, 37480], ['B', 39050, 56190], ['A', 56340, 60640], ['B', 62450, 82950], ['A', 83450, 92540], ['B', 93390, 123314], ['A', 123432, 136440], ['B', 137450, 156910], ['A', 157410, 158990], ['B', 162130, 183634], ['A', 183762, 184886], ['B', 184908, 189078], ['A', 189164, 196540], ['B', 198030, 227638], ['A', 227724, 240330], ['B', 241310, 267770], ['A', 267930, 278600], ['B', 279370, 280340]]
data = utterances

def remove_interval(intervals, removing_interval):
    result = []
    for interval in intervals:
        if interval[1] < removing_interval[0] or interval[0] > removing_interval[1]:
            result.append(interval)
        elif interval[0] < removing_interval[0] and interval[1] > removing_interval[1]:
            result.append([interval[0], removing_interval[0]])
            result.append([removing_interval[1], interval[1]])
        elif interval[0] < removing_interval[0] and interval[1] > removing_interval[0]:
            result.append([interval[0], removing_interval[0]])
        elif interval[0] < removing_interval[1] and interval[1] > removing_interval[1]:
            result.append([removing_interval[1], interval[1]])
    return result

def get_intervals_intersection(interval1, interval2):
    if interval1[1] < interval2[0] or interval2[1] < interval1[0]:
        return []
    else:
        return [[max(interval1[0], interval2[0]), min(interval1[1], interval2[1])]]
    
def get_intervals_intersections(intervals1, intervals2):
    result = []
    for interval1 in intervals1:
        for interval2 in intervals2:
            result.extend(get_intervals_intersection(interval1, interval2))
    return result
    
def get_intervals_union(interval1, interval2):
    if interval1[1] < interval2[0] or interval2[1] < interval1[0]:
        return [interval1, interval2]
    else:
        return [min(interval1[0], interval2[0]), max(interval1[1], interval2[1])]

def detect_no_talk(data, start: int = 0, end: int = functools.reduce(lambda a, b: max(a, b), [x[2] for x in data])):
    no_talk = [[start, end]]
    for i in range(0, len(data)):
        no_talk = remove_interval(no_talk, [data[i][1], data[i][2]])
    return no_talk

def detect_cross_talk(data, start: int = 0, end: int = functools.reduce(lambda a, b: max(a, b), [x[2] for x in data])):
    speakers = functools.reduce(lambda a, b: a | {b[0]: True}, data, {})
    speakers_data = []
    for x in speakers.keys():
        speakers_data.append(list(map(lambda x: [x[1], x[2]], filter(lambda y: y[0] == x, data))))

    if len(speakers_data) <= 1:
        return []

    cross_talk = speakers_data[0]
    for i in range(1, len(speakers_data)):
        cross_talk = get_intervals_intersections(cross_talk, speakers_data[i])
    return cross_talk

print(data)

no_talk = [[x[0] / 1000, x[1] / 1000, (x[1] - x[0]) / 1000] for x in detect_no_talk(data)]
filtered_no_talk = list(filter(lambda x: x[2] > 1, no_talk))
print(filtered_no_talk)

cross_talk = [[x[0] / 1000, x[1] / 1000, (x[1] - x[0]) / 1000] for x in detect_cross_talk(data)]
filtered_cross_talk = list(filter(lambda x: x[2] > 1, cross_talk))
print(filtered_cross_talk)

#print(getIntervalsIntersection([1, 2], [1, 2]))
#print(getIntervalsIntersection([1, 2], [1.5, 2]))
#print(getIntervalsIntersection([1, 1.5], [1, 2]))
#print(getIntervalsIntersection([1, 2], [2, 3]))
#print(getIntervalsIntersection([1, 1.99], [2.01, 3]))
#print(getIntervalsIntersection([1, 2], [1.5, 1.75]))
#print(getIntervalsIntersection([1.5, 1.75], [1, 2]))