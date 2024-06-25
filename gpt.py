import os
import tempfile
from pathlib import Path

from openai import AsyncOpenAI
from config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key)

assistant_id = "asst_hex5KKvql3RzYRwl74Mmv0P7"

vector_store_id = "vs_dSlVnxHfBNrvHOFi4DWhnpBa"


async def speech_to_text(audio_path: str | Path):
    with open(audio_path, "rb") as f:
        audio_file = f
        transcription = await client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return transcription.text


async def text_to_speech(text: str) -> str:
    fd, speech_file_path = tempfile.mkstemp(suffix='.ogg')
    os.close(fd)
    response = await client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    response.stream_to_file(speech_file_path)
    return speech_file_path


async def text_generation(prompt: str) -> (str, str):
    # with open("anxiety.docx", 'rb') as f:
    #     message_file = await client.files.create(
    #         file=f, purpose="assistants"
    #     )

    thread = await client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
                # "attachments": [
                #     {"file_id": message_file.id, "tools": [{"type": "file_search"}]}
                # ],
            }
        ]
    )

    run = await client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )

    if run.status == 'completed':
        messages = await client.beta.threads.messages.list(
            thread_id=thread.id
        )
        message_content = messages.data[0].content[0].text
        annotations = message_content.annotations
        for index, annotation in enumerate(annotations):
            if file_citation := getattr(annotation, "file_citation", None):
                cited_file = await client.files.retrieve(file_citation.file_id)
                message_content.value = message_content.value.replace(annotation.text, f"[{cited_file.filename}]")

        return message_content.value, thread.id



# async def add_file_to_store(file_path: str):
#     with open(file_path, 'rb') as f:
#         file_batch = await client.beta.vector_stores.files.upload_and_poll(
#             vector_store_id=vector_store_id,
#             file=f
#         )
#         print(file_batch)
#
#
# async def update_assistant():
#     await client.beta.assistants.update(
#         assistant_id=assistant_id,
#         description="Ты компаньон который любит отвечать на вопросы и поддерживать диалог. Также все твои сообщения в будущем будут озвучены, поэтому делай ответ законченным и пригодным для озвучки.",
#         instructions="Твои ответы должны быть законченными и удобными к озвучиванию.",
#         model="gpt-3.5-turbo",
#         tools=[{"type": "file_search"}],
#         tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
#     )
#
#
# async def get_assistant():
#     assistant = await client.beta.assistants.retrieve(assistant_id)
#     print(assistant)
#
#
# async def get_vector_store():
#     store = await client.beta.vector_stores.retrieve(vector_store_id=vector_store_id)
#     print(store.file_counts)

# async def delete_vector_store():
#     store = await client.beta.vector_stores.delete(vector_store_id=vector_store_id)
#
#
# async def create_vector_store():
#     vector_store = await client.beta.vector_stores.create(
#         name="Anxiety document"
#     )
#     print(vector_store)

