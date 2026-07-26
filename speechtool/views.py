from django.shortcuts import render
import uuid
import requests
from django.conf import settings
from django.shortcuts import render
from gtts import gTTS
from .forms import AudioUploadForm, TextToSpeechForm

HF_ASR_URL = "https://router.huggingface.co/hf-inference/models/openai/whisper-large-v3"


def index(request):
    transcript = None
    audio_error = None
    speech_url = None
    tts_error = None
    upload_form = AudioUploadForm()
    tts_form = TextToSpeechForm()

    if request.method == 'POST' and request.POST.get('action') == 'transcribe':
      upload_form = AudioUploadForm(request.POST, request.FILES)
    if upload_form.is_valid():
        audio_file = request.FILES['audio']
        audio_bytes = audio_file.read()
        content_type = audio_file.content_type or 'audio/mpeg'

        headers = {
            "Authorization": f"Bearer {settings.HF_API_TOKEN}",
            "Content-Type": content_type,
        }
        response = requests.post(HF_ASR_URL, headers=headers, data=audio_bytes)

        if response.status_code == 200:
            result = response.json()
            transcript = result.get('text', 'No transcript generated')
        else:
            audio_error = f"Error: {response.status_code} - {response.text}"

    if request.method == 'POST' and request.POST.get('action') == 'speak':
        tts_form = TextToSpeechForm(request.POST)
        if tts_form.is_valid():
            text = tts_form.cleaned_data['text']
            try:
                filename = f"{uuid.uuid4().hex}.mp3"
                filepath = settings.MEDIA_ROOT / filename
                settings.MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
                tts = gTTS(text=text, lang='en')
                tts.save(str(filepath))
                speech_url = settings.MEDIA_URL + filename
            except Exception as e:
                tts_error = f"Error generating speech: {str(e)}"

    return render(request, 'index.html', {
        'upload_form': upload_form,
        'tts_form': tts_form,
        'transcript': transcript,
        'audio_error': audio_error,
        'speech_url': speech_url,
        'tts_error': tts_error,
    })

