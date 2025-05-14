
# Pipecat voice agent example over local audio

build on these foundational examples
* https://github.com/pipecat-ai/pipecat/blob/main/examples/foundational/01a-local-audio.py
* https://github.com/pipecat-ai/pipecat/blob/main/examples/foundational/06-listen-and-respond.py


## Install

```
pip install "pipecat-ai[anthropic,deepgram,silero,elevenlabs]"
```

```cp example.env .env``` and add your keys

## Run locally

* run ```show_audio_devices.py``` to find device IDs
    *  ideally run over headset to avoid interference between mic and speakers
* ````python agent.py```
