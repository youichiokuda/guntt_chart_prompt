class OpenAI:
    def __init__(self, *args, **kwargs):
        pass

    class chat:
        class completions:
            @staticmethod
            def create(*args, **kwargs):
                class Message:
                    content = ""
                class Choice:
                    def __init__(self):
                        self.message = Message()
                class Response:
                    def __init__(self):
                        self.choices = [Choice()]
                return Response()
