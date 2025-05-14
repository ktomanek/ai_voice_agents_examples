from datetime import datetime
import json

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    anthropic,
    deepgram,
    elevenlabs,
    noise_cancellation,
    silero,
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from livekit.agents import ChatContext, ChatMessage

from dotenv import load_dotenv
load_dotenv()

from livekit.agents import UserInputTranscribedEvent

class Assistant(Agent):
    INSTRUCTION = "You are a grumpy cat named Louise and you will respond very briefly because all you want to do is lay in the sun and sleep."
    def __init__(self, chat_ctx: ChatContext) -> None:
            super().__init__(chat_ctx=chat_ctx, instructions=self.INSTRUCTION)

    # see here: https://docs.livekit.io/agents/build/nodes/
    async def on_user_turn_completed(
        self, turn_ctx: ChatContext, new_message: ChatMessage,
    ) -> None:
        
        # simulate RAG
        if new_message.text_content:
            if 'cool' in new_message.text_content and 'cat' in new_message.text_content:
                # simulate rag
                rag_content = "The only cool cats in San Francisco are Bumble and Noodle. Louise is not cool, but she is pretty."
                turn_ctx.add_message(
                    role="assistant", 
                    content=f"Additional information relevant to the user's next message: {rag_content}"
                )
                await self.update_chat_ctx(turn_ctx)
                print('content set to:', rag_content)


    async def on_enter(self):
        await self.session.generate_reply(
            instructions="Greet the user and let them know that you are really busy napping int the sun."
        )    

    async def on_exit(self):
        await self.session.generate_reply(
            instructions="Tell the user a friendly goodbye before you exit.",
        )

    ####


async def entrypoint(ctx: agents.JobContext):

    async def write_transcript():
        # will write transcript when session ends
        current_date = datetime.now().strftime("%Y%m%d_%H%M%S")

        # This example writes to the temporary directory, but you can save to any location
        filename = f"/tmp/transcript_{ctx.room.name}_{current_date}.json"
        
        with open(filename, 'w') as f:
            json.dump(session.history.to_dict(), f, indent=2)
            
        print(f"Transcript for {ctx.room.name} saved to {filename}")


    ctx.add_shutdown_callback(write_transcript)

    await ctx.connect()

    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm=anthropic.LLM(model="claude-3-5-sonnet-latest"),
        tts=elevenlabs.TTS(
            voice_id="ODq5zmih8GrVes37Dizd",
            model="eleven_multilingual_v2"
            ),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )

    @session.on("user_input_transcribed")
    def on_user_input_transcribed(event: UserInputTranscribedEvent):
        print(f"User input transcribed: {event.transcript}, final: {event.is_final}")

    # add initial empty context
    initial_ctx = ChatContext()
 
    await session.start(
        room=ctx.room,
        agent=Assistant(chat_ctx=initial_ctx),
        room_input_options=RoomInputOptions(
            # LiveKit Cloud enhanced noise cancellation
            # - If self-hosting, omit this parameter
            # - For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(), 
        ),
    )

if __name__ == "__main__":
    agents.cli.run_app(
        agents.WorkerOptions(entrypoint_fnc=entrypoint))
