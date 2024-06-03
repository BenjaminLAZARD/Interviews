import pytest

from src.loaders.json import CustomJSONLoader


class TestCustomJSONLoader:
    def test_loads_sucessfully(self, tmp_path):
        d = tmp_path / "sub"
        d.mkdir()
        p = d / "hello.json"
        p.write_text(
            """{"language": "fr-FR","jobname": "modjo-zoom-b2a540b4da309e1f","segments": [{"content": "Hello","speaker": "spk2","blockUuid": "9e6a9250-9fd7-4b49-9b76-0df57ec043a6"},{"startTime": 15.58,"endTime": 18.24,"content": "Right back at you","speaker": "spk0","blockUuid": "d340f539-7c41-4a7c-afb7-68b099ef3f70"}]}"""
        )
        print(p.read_text())
        jl = CustomJSONLoader(p)
        docs = jl.load()
        print(docs)
        assert len(docs) == 3
        assert docs[1].page_content == "Hello"
        assert docs[1].metadata["speaker"] == "spk2"
        assert docs[2].page_content == "Right back at you"
        assert docs[2].metadata["speaker"] == "spk0"

    def test_does_not_load_sucessfully(self):
        jl = CustomJSONLoader("dummy.json")
        with pytest.raises(FileNotFoundError):
            jl.load()

    def test_consolidated_text_retranscription(self, tmp_path):
        d = tmp_path / "sub"
        d.mkdir()
        p = d / "hello.json"
        p.write_text(
            """{"language": "fr-FR","jobname": "modjo-zoom-b2a540b4da309e1f","segments": [{"content": "Hello","speaker": "spk2","blockUuid": "9e6a9250-9fd7-4b49-9b76-0df57ec043a6"},{"startTime": 15.58,"endTime": 18.24,"content": "Right back at you","speaker": "spk0","blockUuid": "d340f539-7c41-4a7c-afb7-68b099ef3f70"}]}"""
        )
        print(p.read_text())
        jl = CustomJSONLoader(p)
        transcription = jl.consolidated_text_retranscription()
        assert isinstance(transcription, str)
        assert len(transcription.split("\n- ")) - 1 == 2
        assert len(transcription.split("\n- ")) - 1 == 2
