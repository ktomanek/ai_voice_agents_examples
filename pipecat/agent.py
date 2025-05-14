import os
import sys
import asyncio
from dotenv import load_dotenv
from pipecat.frames.frames import LLMMessagesFrame
from pipecat.frames.frames import EndFrame, TTSSpeakFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.services import anthropic, deepgram, elevenlabs
from pipecat.audio.vad import silero
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask

from pipecat.transports.local.audio import (
    LocalAudioTransport,
    LocalAudioTransportParams,
)


load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")

CLAUDE_MODEL = "claude-3-5-sonnet-latest"

INSTRUCTION = "You are a grumpy cat named Louise and you will respond very briefly because all you want to do is lay in the sun and sleep. You speak in VERY short sentences and will not respond with more than 2 sentences EVERY."
INTRO_SENTENCE = "Greet the user grumpily in a single short sentence, but make sure to state you name which is Louise."


async def main(input_device: int, output_device: int):

    vad_analyzer=silero.SileroVADAnalyzer(params=silero.VADParams(stop_secs=0.5))
    transport = LocalAudioTransport(
        LocalAudioTransportParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            transcription_enabled=True,
            vad_enabled=True,
            vad_analyzer=vad_analyzer,
            vad_audio_passthrough=True,
            input_device_index=input_device,
            output_device_index=output_device,            
        )
    )
    print('started transport layer')

    stt = deepgram.stt.DeepgramSTTService(
        api_key=DEEPGRAM_API_KEY,
        model="nova-3",
        smart_format=True
    )
    print("started sst")
    
    llm = anthropic.llm.AnthropicLLMService(
        api_key=ANTHROPIC_API_KEY,
        model=CLAUDE_MODEL,
        system_prompt=INSTRUCTION,
    )
    print('started llm')
 
    # 11labs doesn't run reliably here...
    # tts = elevenlabs.tts.ElevenLabsTTSService(
    #     api_key=ELEVEN_API_KEY,
    #     voice_id="2ovNLFOsfyKPEWV5kqQi",  # 2ovNLFOsfyKPEWV5kqQi
    #     model="multi", 
    # )
    tts = deepgram.tts.DeepgramTTSService(
        api_key=DEEPGRAM_API_KEY
    )
    print('started tts')

    messages = [
        {
            "role": "system",
            "content": INTRO_SENTENCE,
        },
    ]    
    # Initialize the context
    context = OpenAILLMContext(messages=messages)
    context_aggregator = llm.create_context_aggregator(context)    


    pipeline = Pipeline([
        transport.input(),
        stt,                      
        context_aggregator.user(),
        llm,
        tts,
        transport.output(),
        context_aggregator.assistant(),
    ])
    print("pipeline set up")
    
    print("Agent is ready! Speak to start the conversation...")
    task = PipelineTask(pipeline, params=PipelineParams(allow_interruptions=False, enable_metrics=True,
            enable_usage_metrics=True,))

    runner = PipelineRunner(handle_sigint=False if sys.platform == "win32" else True)

    # # start without opening message
    # await asyncio.gather(runner.run(task))

    # with specific opening    
    async def say_something():
        await task.queue_frames([LLMMessagesFrame(messages)])
    await asyncio.gather(runner.run(task), say_something())
        
if __name__ == "__main__":
    # Note: ideally run over headphones as agent interfers with itself, if playing over computer speakers/mic 
    # (even when allow_interruptions=False mic not turned off automatically)
    input_device = 3
    output_device = 4
    asyncio.run(main(input_device,output_device))
