import json
import os
import re
import secrets
import subprocess

import requests
#for issue contact me ranjanpanpura@gmail.com,https://www.instagram.com/devilfordevs/?hl=en,


class RandomStringGenerator:
    ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"

    @staticmethod
    def generate_content_playback_nonce() -> str:
        return RandomStringGenerator._generate(RandomStringGenerator.ALPHABET, 16)

    @staticmethod
    def generate_t_parameter() -> str:
        return RandomStringGenerator._generate(RandomStringGenerator.ALPHABET, 12)

    @staticmethod
    def _generate(alphabet: str, length: int) -> str:
        return ''.join(secrets.choice(alphabet) for _ in range(length))

class DownloaderApp:
    def get_visitor_id(self) -> str:
        url = "https://youtubei.googleapis.com/youtubei/v1/visitor_id?prettyPrint=false"

        # JSON request body
        json_body = {
            "context": {
                "request": {
                    "internalExperimentFlags": []
                },
                "client": {
                    "androidSdkVersion": 35,
                    "utcOffsetMinutes": 0,
                    "osVersion": "15",
                    "hl": "en-GB",
                    "clientName": "ANDROID",
                    "gl": "GB",
                    "clientScreen": "WATCH",
                    "clientVersion": "19.28.35",
                    "osName": "Android",
                    "platform": "MOBILE"
                },
                "user": {
                    "lockedSafetyMode": False
                }
            }
        }

        headers = {
            "User-Agent": "com.google.android.youtube/19.28.35 (Linux; U; Android 15; GB) gzip",
            "X-Goog-Api-Format-Version": "2",
            "Content-Type": "application/json",
            "Accept-Language": "en-GB, en;q=0.9"
        }

        response = requests.post(url, headers=headers, data=json.dumps(json_body))

        if response.status_code == 200:
            response_json = response.json()
            return response_json["responseContext"]["visitorData"]
        else:
            raise Exception(f"Failed to get visitor ID: {response.status_code} - {response.text}")
    def make_youtube_request(self,video_id):
        self.downloaded_bytes=0
        url = "https://www.youtube.com/youtubei/v1/player"
        data = {
            "context": {
                "client": {
                    "clientName": "IOS",
                    "clientVersion": "19.45.4",
                    "deviceMake": "Apple",
                    "deviceModel": "iPhone16,2",
                    "userAgent": "com.google.ios.youtube/19.45.4 (iPhone16,2; U; CPU iOS 18_1_0 like Mac OS X;)",
                    "osName": "iPhone",
                    "osVersion": "18.1.0.22B83",
                    "hl": "en",
                    "timeZone": "UTC",
                    "utcOffsetMinutes": 0
                }
            },
            "videoId": video_id,
            "playbackContext": {
                "contentPlaybackContext": {
                    "html5Preference": "HTML5_PREF_WANTS",
                    "signatureTimestamp": 20052
                }
            },
            "contentCheckOk": True,
            "racyCheckOk": True
        }
        headers = {
            'X-YouTube-Client-Name': '5',
            'X-YouTube-Client-Version': '19.45.4',
            'Origin': 'https://www.youtube.com',
            'User-Agent': 'com.google.ios.youtube/19.45.4 (iPhone16,2; U; CPU iOS 18_1_0 like Mac OS X;)',
            'content-type': 'application/json',
            'X-Goog-Visitor-Id': 'Cgt6VVhqY0RwaE9JWSizjZq6BjIKCgJJThIEGgAgHw%3D%3D'
        }
        query = {'prettyPrint': 'false'}

        try:
            response = requests.post(
                url,
                params=query,
                headers=headers,
                data=json.dumps(data)  # Convert the Python dictionary to a JSON string
            )
            response.raise_for_status()  # Raise an error for HTTP errors (4xx or 5xx)
            return response.json()  # Return the JSON response
        except requests.exceptions.RequestException as e:
            print(f"Error making request: {e}")
            return None

    def download_as_9mb(self,url: str, fos,total_bytes: int):
        chunk_size = 9437184  # 9 MB
        end_byte = min(self.downloaded_bytes + chunk_size, total_bytes) - 1  # Range is inclusive

        headers = {
            "Range": f"bytes={self.downloaded_bytes}-{end_byte}"
        }

        response = requests.get(url, headers=headers, stream=True)

        if response.status_code in (200, 206):
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    fos.write(chunk)
                    self.downloaded_bytes += len(chunk)
                    print(f"\r{self.convert_bytes(self.downloaded_bytes)}/{self.convert_bytes(total_bytes)}",end="")

        if self.downloaded_bytes==total_bytes:
            print("\nDownloaded All Bytes")
        else:
            self.download_as_9mb(url,fos,total_bytes)



    def convert_bytes(self,size_in_bytes: int) -> str:
        kilobyte = 1024
        megabyte = kilobyte * 1024
        gigabyte = megabyte * 1024

        if size_in_bytes >= gigabyte:
            return f"{size_in_bytes / gigabyte:.2f} GB"
        elif size_in_bytes >= megabyte:
            return f"{size_in_bytes / megabyte:.2f} MB"
        elif size_in_bytes >= kilobyte:
            return f"{size_in_bytes / kilobyte:.2f} KB"
        else:
            return f"{size_in_bytes} Bytes"

    def txt2filename(self,txt: str) -> str:
        special_characters = [
            "@", "#", "$", "*", "&", "<", ">", "/", "\b", "|", "?", "CON", "PRN", "AUX", "NUL",
            "COM0", "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9", "LPT0",
            "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9", ":", "\"", "'"
        ]

        normal_string = txt
        for sc in special_characters:
            normal_string = normal_string.replace(sc, "")

        return normal_string

    def merge_video_audio(self, audio: str, video: str, final: str) -> bool:
        cmd = [
            "ffmpeg",
            "-i", video,
            "-i", audio,
            "-c:v", "copy",
            "-y",
            "-map", "0:v:0",
            "-map", "1:a:0",
            final
        ]

        process = subprocess.Popen(
            cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True,encoding="utf-8"
        )

        progress_regex = re.compile(r"time=([\d:.]+)")
        duration_regex = re.compile(r"Duration: ([\d:.]+),")

        total_duration = None
        while True:
            line = process.stderr.readline()
            if not line:
                break

            # Get total duration
            if total_duration is None:
                duration_match = duration_regex.search(line)
                if duration_match:
                    total_duration = duration_match.group(1)

            # Get progress
            progress_match = progress_regex.search(line)
            if progress_match:
                progress = progress_match.group(1)
                if total_duration:
                    print(f"\rMerging: {progress}/{total_duration}", end="")

        # Wait for the process to ensure ffmpeg has released the files
        success = process.wait() == 0
        return success


    def extract_video_id(self,yt_url: str) -> str | None:
        regex = r"""^.*(?:(?:youtu\.be\/|v\/|vi\/|u\/\w\/|embed\/|shorts\/|live\/)|(?:(?:watch)?\?v(?:i)?=|\&v(?:i)?=))([^#\&\?]*).*"""
        match_result = re.match(regex, yt_url)
        if match_result:
            return match_result.group(1)
        return None

    def android_player_response(self,cpn: str, visitor_data: str, video_id: str, t: str) -> requests.Response:
        url = f"https://youtubei.googleapis.com/youtubei/v1/reel/reel_item_watch?prettyPrint=false&t={t}&id={video_id}&fields=playerResponse"

        # JSON request body
        json_body = {
            "cpn": cpn,
            "contentCheckOk": True,
            "context": {
                "request": {
                    "internalExperimentFlags": []
                },
                "client": {
                    "androidSdkVersion": 35,
                    "utcOffsetMinutes": 0,
                    "osVersion": "15",
                    "hl": "en-GB",
                    "clientName": "ANDROID",
                    "gl": "GB",
                    "clientScreen": "WATCH",
                    "clientVersion": "19.28.35",
                    "osName": "Android",
                    "platform": "MOBILE",
                    "visitorData": visitor_data
                },
                "user": {
                    "lockedSafetyMode": False
                }
            },
            "racyCheckOk": True,
            "videoId": video_id,
            "playerRequest": {
                "videoId": video_id
            },
            "disablePlayerResponse": False
        }

        # Request headers
        headers = {
            "User-Agent": "com.google.android.youtube/19.28.35 (Linux; U; Android 15; GB) gzip",
            "X-Goog-Api-Format-Version": "2",
            "Content-Type": "application/json",
            "Accept-Language": "en-GB, en;q=0.9"
        }

        # Send the request
        response = requests.post(url, headers=headers, data=json.dumps(json_body))

        return response
    def startFuction(self):
        urlInput = input("\nEnter Youtube Url >>>")
        videoId = self.extract_video_id(urlInput)
        #visitor id or data expected by youtube in every request for streamingData
        visitor_data = self.get_visitor_id()
        #cpn or nonce string will return in each format url
        cpn = RandomStringGenerator.generate_content_playback_nonce()
        #t parameter used for what i dont know
        tp = RandomStringGenerator.generate_t_parameter()
        response = self.android_player_response(cpn, visitor_data, videoId, tp)
        #here the json returned has extra key(PlayerResponse) as compared to ios client
        responsYt = response.json()["playerResponse"]
        title = self.txt2filename(responsYt["videoDetails"]["title"])
        print(title)
        fmts = responsYt["streamingData"]["adaptiveFormats"]
        for fmt in fmts:
            if "audio" in fmt["mimeType"]:
                item = str(fmt["itag"]) + "   " + self.convert_bytes(fmt["bitrate"]) + "/s   " + self.convert_bytes(
                    int(fmt["contentLength"]))
                print(item)
            if "video" in fmt["mimeType"]:
                item = str(fmt["itag"]) + "   " + fmt["qualityLabel"] + "    " + self.convert_bytes(
                    int(fmt["contentLength"]))
                print(item)
        enteredItag = input("Enter Itag >>>")
        itag = int(enteredItag)
        for fmt in fmts:
            self.downloaded_bytes = 0
            if itag == fmt["itag"]:
                downloads_folder = os.path.join(os.environ['USERPROFILE'], 'Downloads')
                if "audio" in fmt["mimeType"]:
                    file_name = f"{title}.mp3"
                    file_path = os.path.join(downloads_folder, file_name)
                    print(file_path)
                    Audiofile = open(file_path, "wb")
                    print("Downloading Audio")
                    self.download_as_9mb(fmt["url"], Audiofile, int(fmt["contentLength"]))
                    self.startFuction()
                else:
                    file_name = f"{title}({itag}).mp4"
                    file_path = os.path.join(downloads_folder, file_name)
                    file = open("temp.mp4", "wb")
                    print("Downloading Video")
                    self.download_as_9mb(fmt["url"], file, int(fmt["contentLength"]))
                    print("Downloading Audio")
                    for fmaudio in fmts:
                        if fmaudio["itag"] == 251:
                            Audiofile = open("temp.mp3", "wb")
                            self.downloaded_bytes = 0
                            self.download_as_9mb(fmaudio["url"], Audiofile, int(fmaudio["contentLength"]))
                            print("Going To Merge")
                            self.merge_video_audio(Audiofile.name, file.name, file_path)
                            self.startFuction()
        print("Format Not Avaible")
        self.startFuction()


app=DownloaderApp()
app.startFuction()