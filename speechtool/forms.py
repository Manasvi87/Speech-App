from django import forms

class AudioUploadForm(forms.Form):
    audio = forms.FileField()

class TextToSpeechForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea, max_length=1000)