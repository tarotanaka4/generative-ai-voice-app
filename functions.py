import os
from pydub import AudioSegment
import time
from time import sleep
from scipy.io.wavfile import write
from pathlib import Path
import streamlit as st
from audiorecorder import audiorecorder
import glob

def delete_wav_files():
    dirs=["audio/input","audio/output"]
    for dir in dirs:
        audio_directory = Path.cwd() / dir
        # フォルダ内のすべての.wavファイルを取得
        wav_files = glob.glob(os.path.join(audio_directory, '*.wav'))
        
        # それぞれのファイルを削除
        for file in wav_files:
            os.remove(file)
            print(f"{file} を削除しました")
    
    print("すべての.wavファイルを削除しました")
    
def record_audio(fs=48000, dir="audio/input", silence_threshold=2.5, min_duration=0.05, amplitude_threshold=0.01):
    audio_directory = Path.cwd() / dir
    audio_directory.mkdir(parents=True, exist_ok=True)
    file_path = audio_directory / f"recorded_audio_input_{int(time.time())}.wav"

    audio = audiorecorder("発話を開始します", "発話が終わったら停止してください",start_style={'color':'black'}, stop_style={'color':'blue','background-color':'red'})

    if len(audio) > 0:
        # To save audio to a file, use pydub export method:
        audio.export(file_path, format="wav")
    else:
        st.stop()
    return file_path

def transcribe(file_path, client):
    with open(file_path, 'rb') as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return transcript

def save_to_wav(response_content, output_file):
    """
    mp3形式の音声ファイルをwav形式に変換して保存
    """
    temp_file_name = "temp.mp3"
    with open(temp_file_name, "wb") as temp_file:
        temp_file.write(response_content)
    
    audio = AudioSegment.from_file(temp_file_name, format="mp3")
    audio.export(output_file, format="wav")

    # 一時ファイルを削除
    os.remove(temp_file_name)

# カスタムCSSを追加してst.audioを非表示にする
def add_custom_css():
    st.markdown(
        """
        <style>
        .stAudio {
            display: none;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

def play_wav(filepath, speed=1.0, stop=False):
    """
    音声ファイルの読み上げ
    Args:
        file_path: 音声ファイルのパス
        speed: 再生速度（1.0が通常速度、0.5で半分の速さ、2.0で倍速など）
    """
    # PyDubで音声ファイルを読み込む
    audio = AudioSegment.from_wav(filepath)
    
    # 速度を変更
    if speed != 1.0:
        # frame_rateを変更することで速度を調整
        modified_audio = audio._spawn(audio.raw_data, overrides={
            "frame_rate": int(audio.frame_rate * speed)
        })
        # 元のframe_rateに戻す（ピッチを保持したまま速度だけ変更）
        modified_audio = modified_audio.set_frame_rate(audio.frame_rate)
    else:
        modified_audio = audio

    # 一時ファイルとして保存
    temp_file = "temp_modified.wav"
    modified_audio.export(temp_file, format="wav")
    
    # カスタムCSSを適用する
    add_custom_css()

    # st.audioで再生
    st.audio(temp_file, format='audio/wav', autoplay=True)
    if stop:
        st.stop()

    # 一時ファイルを削除
    os.remove(temp_file)