import subprocess
import os
import tempfile
import csv

from google.cloud import speech
from google.cloud import storage

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/home/kwisatz/pr/key.json"

storage_client = storage.Client()
client = speech.SpeechClient()

def list_blobs(bucket_name):
    blobs = storage_client.list_blobs(bucket_name)
    return blobs

def upload_to_bucket(blob_name, file_path, bucket_name):
    bucket = storage_client.get_bucket('pr_files_to_transcript')
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(file_path)

temp_dir = tempfile.TemporaryDirectory()
f1 = temp_dir.name
wave_dir_path = temp_dir.name + "/test_wavs"


subprocess.run("sshpass -p P8TbXQch sftp -r internship@185.110.50.61:/test_wavs " + f1, shell=True)


dirs = os.listdir(wave_dir_path)

for index, file in enumerate(dirs):
    upload_to_bucket("plik" + str(index + 1), os.path.join(wave_dir_path, file), 'pr_files_to_transcript')


#Posortować listę


my_bucket = list_blobs('pr_files_to_transcript')

for file in my_bucket:
    
    gcs_uri = "gs://pr_files_to_transcript/" + str(file.name)
    
    audio = speech.RecognitionAudio(uri=gcs_uri)
    
    config = speech.RecognitionConfig(
       encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
       sample_rate_hertz=16000,
       language_code="en-US",
    )
    
    response = client.recognize(config=config, audio=audio)
    
    for result in response.results:
        
        print(str(format(result.alternatives[0].transcript)))
        
        wynik = format(result.alternatives[0].transcript)
        
        with open('pr/wyniki.csv', 'a', encoding='UTF8') as wyniki:
            writer = csv.writer(wyniki)
            writer.writerow([wynik])


# def download_file_from_bucket(blob_name, file_path, bucket_name):
#         bucket = storage_client.get_bucket('pr_files_to_transcript')
#         blob = bucket.blob(blob_name)
#         with open(file_path, 'wb') as f:
#             storage_client.download_blob_to_file(blob, f)
