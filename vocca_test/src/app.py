import asyncio
import os
import sys
from datetime import datetime
from typing import TypedDict

import aiohttp
from deepgram import LiveOptions
from dotenv import load_dotenv
from loguru import logger
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.services.cartesia import CartesiaTTSService
from pipecat.services.deepgram import DeepgramSTTService
from pipecat.services.google import GoogleLLMService
# from pipecat.utils.text.markdown_text_filter import MarkdownTextFilter
from pipecat.transcriptions.language import Language
from pipecat.transports.services.daily import DailyParams, DailyTransport
from pipecat_flows import FlowArgs, FlowConfig, FlowManager

load_dotenv(override=True)

logger.remove(0)
logger.add(sys.stderr, level="DEBUG")


# Type definitions for API responses
class Patient(TypedDict):
    first_name: str
    last_name: str


class Meeting(TypedDict):
    type: str  # Literal["dentist", "orthodontist", "other"]
    year: int
    month: int
    day: int
    hour: int
    min: int
    patient: Patient


PATIENT = Patient(first_name="", last_name="")
dummy_date = datetime.strptime("1000-01-01 00:00", "%Y-%m-%d %H:%M")
MEETING = Meeting(
    type="other",
    year=int(dummy_date.year),
    month=dummy_date.month,
    day=dummy_date.day,
    hour=dummy_date.time().hour,
    min=dummy_date.time().minute,
    patient=PATIENT,
)


async def register_patient(args: FlowArgs):
    print(args.keys())
    print(args["first_name"])
    PATIENT["first_name"] = args["first_name"]
    PATIENT["last_name"] = args["last_name"]
    return PATIENT


async def register_meeting_type(args: FlowArgs):
    MEETING["meeting_type"] = args["meeting_type"]
    print(MEETING["meeting_type"])
    return MEETING


async def register_meeting_date(args: FlowArgs):
    date = datetime.strptime(args["date"], "%Y-%m-%d %H:%M")
    MEETING = Meeting(
        type="other",
        year=date.year,
        month=date.month,
        day=date.day,
        hour=dummy_date.time().hour,
        min=dummy_date.time().minute,
        patient=PATIENT,
    )
    return MEETING


# Flow configuration
flow_config: FlowConfig = {
    "initial_node": "greeting",
    "nodes": {
        "greeting": {
            "role_messages": [
                {
                    "role": "system",
                    "content": "Vous êtes un assistant pour prendre des rendez-vous dans un cabinet de dentistes. Votre prénom est Jeanne. Vos réponses seront converties en audio lors d'une conversation telephonique. Adoptez un ton sympathique, mais utilisez le vouvoiement. Utilisez toujours les fonctions disponibles pour faire progresser la conversation naturellement.Vous parlez exclusivement Français mais vous comprenez d'autres langues au besoin.",
                }
            ],
            "task_messages": [
                {
                    "role": "system",
                    "content": "Vous êtes un assistant pour prendre des rendez-vous. Commencez la conversation en saluant l'utilisateur,"
                    "et en expliquant que le but est de prendre un rdv medical au cabinet 'La vie est belle' à Toulouse."
                    "Ensuite, demander à l'utilisateur son nom. Clarifier au besoin le prénom et le nom. Ne pas hésiter à demander confirmation à l'utilisateur et attendre son retour pour enregistrer le resultat."
                    "Enregistrer le resultat à l'aide de la fonction register_patient une fois le prénom et nom confirmés."
                    "Passer ensuite au choix du type de rdv",
                }
            ],
            "functions": [
                {
                    "function_declarations": [
                        {
                            "name": "register_patient",
                            "handler": register_patient,
                            "description": "Enregistrer le prenom et nom du patient",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "first_name": {
                                        "type": "string",
                                        "description": "First Name of the user",
                                    },
                                    "last_name": {
                                        "type": "string",
                                        "description": "Last Name of the user",
                                    },
                                },
                                "required": ["first_name", "last_name"],
                            },
                            "transition_to": "select_meeting_type",
                        },
                    ]
                }
            ],
        },
        "select_meeting_type": {
            "task_messages": [
                {
                    "role": "system",
                    "content": """Demandez à l'utilisateur s'il souhaite un rendez-vous chez le dentiste ou l'orthodontiste, ou un autre type de rdv. Explicitez les types de rdv possibles. Ne pas hésiter à demander confirmation à l'utilisateur en répétant son choix avant d'enregistrer le type de rdv, et attendre son retour et eventuelle correction avant d'enregistrer le resultat avec la fonction register_meeting_type. Enregistrer le resultat à l'aide de la fonction register_meeting_type.""",
                }
            ],
            "functions": [
                {
                    "function_declarations": [
                        {
                            "name": "register_meeting_type",
                            "handler": register_meeting_type,
                            "description": "Comprendre le type de rdv parmi les choix possibles: dentiste, orthodontiste, autre",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "meeting_type": {
                                        "type": "string",
                                        "description": "Type of meeting, one of ['dentist', 'orthodontist', 'other'']",
                                    }
                                },
                                "required": ["meeting_type"],
                            },
                            "transition_to": "select_meeting_date",
                        },
                    ]
                }
            ],
        },
        "select_meeting_date": {
            "task_messages": [
                {
                    "role": "system",
                    "content": "Demandez à l'utilisateur la date et l'heure du rendez-vous souhaitée. Demandez confirmation et valider avec l'utilisateur en repetant son choix. Enregistrer avec la fonction register_meeting_date la date du rdv. Ne pas imposer de format spécifique au client, c'est à toi de convertir au format '%Y-%m-%d %H:%M', mais tu ne dois pas demander au client de le faire",
                }
            ],
            "functions": [
                {
                    "function_declarations": [
                        {
                            "name": "register_meeting_date",
                            "handler": register_meeting_date,
                            "description": "Enregistrer la date et l'heure du rendez-vous.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "date": {
                                        "type": "string",
                                        "description": "date et heure du rdv au format datetime '%Y-%m-%d %H:%M'",
                                    }
                                },
                                "required": ["date"],
                            },
                            "transition_to": "end",
                        },
                    ],
                },
            ],
        },
        "end": {
            "task_messages": [
                {
                    "role": "system",
                    "content": "Remerciez chaleureusement l'utilisateur et mentionnez qu'il peut revenir à tout moment pour prendre un autre rdv.",
                }
            ],
            "functions": [],
            "post_actions": [{"type": "end_conversation"}],
        },
    },
}


async def main():
    """Main function to set up and run the movie explorer bot."""
    async with aiohttp.ClientSession() as session:
        room_url = "https://v-test-app.daily.co/v_test"

        transport = DailyTransport(
            room_url,
            None,
            "Movie Explorer Bot",
            DailyParams(
                audio_out_enabled=True,
                vad_enabled=True,
                vad_analyzer=SileroVADAnalyzer(),
                vad_audio_passthrough=True,
                transcription_enabled=True,
            ),
        )

        # stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))
        # tts = CartesiaTTSService(
        #     api_key=os.getenv("CARTESIA_API_KEY"),
        #     voice_id="c45bc5ec-dc68-4feb-8829-6e6b2748095d",  # Movieman
        #     text_filter=MarkdownTextFilter(),
        # )
        stt = DeepgramSTTService(
            api_key=os.getenv("DEEPGRAM_API_KEY"),
            language=Language.FR_FR,
            voice="nova-2",
            live_options=LiveOptions(
                # encoding="linear16",
                language=Language.FR_FR,
                model="nova-2-general",
                # sample_rate=16000,
                # channels=1,
                # interim_results=True,
                # smart_format=True,
                punctuate=True,
                # profanity_filter=False,
                # vad_events=False,
            ),
        )
        tts = CartesiaTTSService(
            api_key=os.getenv("CARTESIA_API_KEY"),
            voice_id="8832a0b5-47b2-4751-bb22-6a8e2149303d",
            language=Language.FR,
            params=CartesiaTTSService.InputParams(
                language=Language.FR,
                speed="normal",
                model="sonic",
                emotion=["positivity:high", "curiosity"],
            ),
        )
        # tts = GoogleTTSService(
        #     credentials_path="path/to/credentials.json",
        #     voice_id="fr-FR-Wavenet-F",
        #     params=GoogleTTSService.InputParams(
        #         language=Language.FR,
        #         gender="female",
        #         google_style="empathetic"
        #     )
        # )
        llm = GoogleLLMService(
            api_key=os.getenv("GOOGLE_GEMINI_API_KEY"),
            params=GoogleLLMService.InputParams(extra={"language": "french"}),
            language=Language.FR,
        )

        context = OpenAILLMContext()
        context_aggregator = llm.create_context_aggregator(context)

        pipeline = Pipeline(
            [
                transport.input(),  # Transport user input
                stt,  # STT
                context_aggregator.user(),  # User responses
                llm,  # LLM
                tts,  # TTS
                transport.output(),  # Transport bot output
                context_aggregator.assistant(),  # Assistant spoken responses
            ]
        )

        task = PipelineTask(pipeline, PipelineParams(allow_interruptions=True))

        # Initialize flow manager
        flow_manager = FlowManager(task=task, llm=llm, tts=tts, flow_config=flow_config)

        @transport.event_handler("on_first_participant_joined")
        async def on_first_participant_joined(transport, participant):
            await transport.capture_participant_transcription(participant["id"])
            await flow_manager.initialize()
            await task.queue_frames([context_aggregator.user().get_context_frame()])

        runner = PipelineRunner()
        await runner.run(task)

        print(PATIENT)
        print(MEETING)


if __name__ == "__main__":
    asyncio.run(main())
