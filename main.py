# @title <font color=teal> 🖥️ Main Colab Leech Code

# @title Main Code

API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"
BOT_TOKEN = "7772724138:AAHGfrzxM9RFmOzhbqqeEyRhrUeJuUJ698g"  # @param {type: "string"}
USER_ID = 121110934
DUMP_ID = -1001593908646  # @param {type: "integer"}

import subprocess, time, shutil, os
from IPython.display import clear_output, display, HTML
from threading import Thread

Working = True

banner = '''
    _________          .___     ________/\\
   / _____/____    __| _/____ \_____ )/ ______
  \_____ \__  \  / __ |/ __ \ / / \ \ / ___/
  /      \/ __ \/ /_/ \ ___// \_/. \\___ \
 /_______ (____ |____ |\___ >_____\ \_/____ >
          \/    \/     \/      \__>    \/

 _________        .__       ___.
 \_ ___ \ ____ | | _____ \_ |__
 / \ \ / / _ \| | \__ \ | __ \
 \ \ _( <_> ) |__/ __ \| \_\ \
  \______ /\____/|____(____ /___ /
          \/              \/    \/

 ____                  .__
 |    | ____ ____ ____ | |__  ___________
 |    |_/ __ \/ __ \/ ___\| | \_/ __ \_ __ \
 |    __\ ___| ___| \___| Y \ ___| | \/
 |______ \___ >___ >___ >___| /\___ >__|
        \/    \/    \/    \/    \/

 /\
 \/
'''

display(HTML(f'<pre>{banner}</pre>'))

def keep_alive(url):
    display(HTML(f'<audio src="{url}" controls autoplay style="display:none"></audio>'))

def Loading():
    white = 37
    black = 0
    progress_html = "<div style='width: 100%; background-color: #e0e0e0; height: 20px; border-radius: 10px;'><div id='progress' style='height: 100%; width: 0%; background-color: #76c7c0; border-radius: 10px;'></div></div>"
    display(HTML(progress_html))

    while Working:
        black = (black + 2) % 75
        white = (white - 1) if white != 0 else 37
        progress = (white * 100) // 37  # Normalize to get the progress percentage
        display(HTML(f"<script>document.getElementById('progress').style.width = '{progress}%';</script>"))
        time.sleep(2)
    clear_output()

audio_url = "https://raw.githubusercontent.com/KoboldAI/KoboldAI-Client/main/colab/silence.m4a"
audio_thread = Thread(target=keep_alive, args=(audio_url,))
audio_thread.start()

_Thread = Thread(target=Loading, name="Prepare", args=())
_Thread.start()

if len(str(DUMP_ID)) == 10 and "-100" not in str(DUMP_ID):
    n_dump = "-100" + str(DUMP_ID)
    DUMP_ID = int(n_dump)

def setup():
    global Working
    try:
        if os.path.exists("/content/sample_data"):
            shutil.rmtree("/content/sample_data")

        cmd = "git clone https://github.com/thesadeq/Telegram-Leecher"
        subprocess.run(cmd, shell=True, check=True)

        cmd = "bash /content/Telegram-Leecher/setup.sh"
        subprocess.run(cmd, shell=True, check=True)

        cmd = "apt update && apt install ffmpeg aria2 megatools -y"
        subprocess.run(cmd, shell=True, check=True)

        cmd = "pip3 install -r /content/Telegram-Leecher/requirements.txt"
        subprocess.run(cmd, shell=True, check=True)

        # Set environment variables
        os.environ["API_ID"] = str(API_ID)
        os.environ["API_HASH"] = API_HASH
        os.environ["BOT_TOKEN"] = BOT_TOKEN
        os.environ["USER_ID"] = str(USER_ID)
        os.environ["DUMP_ID"] = str(DUMP_ID)

        if os.path.exists("/content/Telegram-Leecher/my_bot.session"):
            os.remove("/content/Telegram-Leecher/my_bot.session")

        print("\rStarting Bot....")
    except subprocess.CalledProcessError as e:
        print(f"Error during setup: {e}")
        Working = False
        return
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        Working = False
        return
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        Working = False
        return
    Working = False

setup()

if "API_ID" in os.environ:
    !cd /content/Telegram-Leecher/ && python3 -m colab_leecher # type:ignore
else:
    print("Setup failed, bot not started.")
