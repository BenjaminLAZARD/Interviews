# Voice conversational assistant

## Problem

We want to create a voice-conversational chat interface as described in [assignment.md](assignment.md).

## Constraints

- Assuming language is english for now
- hardware and structure that can be used to train such a model (check out groq)
- speed/latency
- cloud or local?

## Components needed

- An interface to continuously listen to a user
- An interface to output a video
- A conversational tool LLM-like
- speech-to-text capabilities (with live streaming)
- text-to-video capabilities
- An "orchestrator" of some sort to understand when to listen to the use vs when to answer a prompt (when is the start/end) and when to start transcribing to video

## Research

- According to ChatGpt without surprise "creating a voice asssistant in <4h is quite ambitious"

### Potential technologies for integrated chat

- Google's DialogFlow, Amazon's Lex, Micrsofot Bot, Rasa. These are pre-made solutions requiring limited tech knowledge.

- Nvidia's Omniverse virtual assistant seems promising. I won't spend time installing everything on my own machine as it requires an "omniverse server" to be running in the background. This is a proprietary system and requires some level of investment in time.
[End-to-End Speech AI Pipelines presentation](https://resources.nvidia.com/en-us-speech-ai-ebooks-gated/speech-ai-using-asr-and-tts)
[Omniverse Set Up](https://github.com/metaiintw/build-an-avatar-with-ASR-TTS-Transformer-Omniverse-Audio2Face)
[Python tutorial](https://github.com/metaiintw/build-an-avatar-with-ASR-TTS-Transformer-Omniverse-Audio2Face/blob/main/1.Create_A_Simple_Avatar/1.Creating_a_simple_avatar.ipynb)

### LLM component to be used

- GPT-4: good, API call possible, but costly, not easy to fine-tune
- Falcon: good, but ver heavy hardware-wise
- LLama2: good although not as good as the previous ones, opensource, comes in various sizes and flavours. Q4_K_M weighs only 4 Gb and requires <7Gb RAM which amkes it runnable on a modern local machine.
- Vicuna: licence is opensource but non commercial...
- Mistral 8 x7B: potentially better than LLama2 for a given size.  Q4_K_M weighs only 4.4 Gb and requires <7Gb RAM which amkes it runnable on a modern local machine.

### Speech-to-text

- Whisper -> oepn ai team validated, opensource. Excells not only in English. Very simple python API, comes in various model sizes. The only worry here is future development as OpenAI may no longer maintain it or change licence type and it may become a source of costs. API is very simple cf [tutorial](https://billtcheng2013.medium.com/faster-audio-transcribing-with-openai-whisper-and-huggingface-transformers-dc088243803d).
- CMU Sphinx -> Good, fast, but less documented. [Good streaming API](https://www.geeksforgeeks.org/speech-recognition-in-python-using-cmu-sphinx/)
- Kaldi -> higher quality, more customizable but potentially harder to set up
- Mozilla Deepspeech -> good standard solution, opensource by design. It relies on tensorflow instead of pytorch which is not great given the standards in the industry and other parts of this exercise's dependencies. API is not super easy to manage and may be a bit older, yet it supports streaming apparently better than whisper.
- Julius -> more japanese oriented
- Wit.ai -> more adpated to standalone files

### Text-to-video

It is actually extremely difficult to find such libraries.

- Existing solutions are actually companies by themselves such as Synthesia.
- There exist various github repositories that seem rather experimental that aim to
  - perform some sort of lip-synching (implying possession of images or video records of a given person). [Wav2Lip tutorial](https://medium.com/@sornatk/deepfake-video-with-custom-text-and-original-voice-made-easily-32e602644773).
  - perform video2video conversion. The best documented case being the deepfake libraries.
  - perform audio2video conversion given just an image. [MakeItTalk tutorial](https://github.com/yzhou359/MakeItTalk). Quality isn't amazing but you can have a character or real person speak a long speech [video example](https://www.youtube.com/watch?v=wu7FJBAc-xo).

### Orchestrator

- Voice Activity Detection is available as part of DeepSpeech. cf [this tutorial](https://github.com/mozilla/DeepSpeech-examples/blob/r0.9/mic_vad_streaming/mic_vad_streaming.py)
- Whisper does not come with VAD, but some [extra work can help](https://github.com/openai/whisper/discussions/397) using Silvero VAD for exemple.
- Then techniques like silence detection, Turn-talking or NLU (to understand start and stop of the prompt must be used)

## Solutions retained

- Llama2 and its many flavours seem like a good start compared to alternatives like Falcon, GPT, etc because it is open-source, have a good relative performance, and its many flavours make it easier to adapt to hardware needs (Flacon for exemple is very heavy) when training. It is often quite time-consuming
After some research, use of quantization can make model small enough so that they can run on a single jupyter collab notebook for example HuggingFace's "TheBloke/Llama-2-7b-Chat-GGUF". Recently though Mistral delivered a slightly better performance (weight and RAM being the same) <https://huggingface.co/TheBloke/Mistral-Trismegistus-7B-GGUF> -> Q4KM

- Whisper

- Turtoise TTS + Google TTS

- text-to-video capabilities: we will pick MaKeItTalk as it is more suitable for a long-exchange. This requires going from text to audio first.

- Orchestration
  - We use Mozilla Deepseech continuous streaming from microphone
  - To make things simple for starters we will use a simple 2s silence detection to read from buffer and actually run the LLM model on the detected prompt then reset the model
  - Then we will ship this to the video avatar generator

## Deployment / Hardware

- To use pre-trained models, a good GPU (T4) per user may be sufficient. For training a bigger resource may be needed like A100/A6000. Potentially Google's TPUs. Newest H100 may be considered. Groq LPU may not outperform A100 for complex AI tasks but still work in similar conditions.
- \> 2^7 Gb RAM would be beneficial.
- An Web-like API is necessary therefore servers or a cloud architecture would be needed.

## Actual code

While implementing, the following came up:

- deepspeech does not seem maintained anymore. So I switched to Whisper and an external VAD called Silero as found in the [tutorial mentioned above](#solutions-retained). The only problem is that it does not support live streaming. I could potentially combine it with [external solutions](https://www.youtube.com/watch?v=zqp_hVZTd-g)...
- I have a slow internet connection and an old GPU so I had to turn to external resources. Jupyter Colab failed me as we can only use so many GPU hours. I discovered a new solution: Saturn Cloud. It offers 10h per month free of charge and you can connect over ssh.
- Altough I found no clear explanations on the web, I decided to go with a Gemini's suggested approach: using an audio stream would be compatible with whisper... But this time I ran into another problem. Because I am runing a notebook in the cloud, I don't have access to my own machine microphone. I decided to skip this part for now.
- I downloaded the latest librbaries and because of that had to make some small changes to the repositories I used (mentioned in the notebook).
- Resizing to appropriate size the source image for the avatar was needed.

Checkout the [notebook](digital_dandelion_notebook.ipynb)

Now of course there still remains the not so easy task to put it all together...

Audio streaming and understanding is relatively easy. Animating an avatar with a given reply is not that fast thouh.

## Potential improvements

- Make it a proper repository with requirements
- Clear Documentation
- Testing: having a proper framework to evaluate model performance from end-to-end starting with simple unit-testing.
- building a proper front-end solution
- further training/fine-tuning
- find a more suitable solution for avatar video generation. The one picked is quite bare-metal.
- Integrate with proper web development? [code](https://github.com/deepgram-devs/live-transcription-fastapi)
- Find ways to generate the avatar faster?

## Notes

- Using ChatGPT to find the right tool is really bad. It tried to attach "speech-to-video" to lip-synch and video editing when what I was really looking for was closer to deepfakes.
- Gemini proved a bit better at understanding simple coding questions.
