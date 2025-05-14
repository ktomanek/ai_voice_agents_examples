

demo based on LiveKit VoiceAI Quickstart

* https://docs.livekit.io/agents/start/voice-ai/


# Install

## authenticate

```cp example.env .env``` and add your keys

## deps

```
pip install \
  "livekit-agents[deepgram,anthropic,silero,turn-detector]~=1.0" \
  "livekit-plugins-noise-cancellation~=0.2" \
  "python-dotenv"
```

# Run

##  download models  (vad, noise cancelation, turn detection) 

```python agent.py download-files```

## run on console

```python agent.py console```

## run with PlayGround

* connect to playground: ```python agent.py dev```
* then open  agent in playground: https://agents-playground.livekit.io/

(see details: https://docs.livekit.io/agents/start/playground/)

