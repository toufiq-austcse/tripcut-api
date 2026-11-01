class DirectorError(Exception):
    """The LLM director failed or returned an invalid edit list; the caller falls back.

    Carries the tokens already spent so metrics.json still shows the real cost.
    """

    def __init__(self, message: str, tokens_in: int = 0, tokens_out: int = 0) -> None:
        super().__init__(message)
        self.tokens_in = tokens_in
        self.tokens_out = tokens_out
