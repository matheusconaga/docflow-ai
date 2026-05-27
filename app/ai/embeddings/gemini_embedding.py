import time

from google import genai
from google.genai.errors import ClientError, ServerError

from app.core.config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)


class GeminiEmbedding:

    @staticmethod
    def generate(text: str, retries: int = 3):

        for attempt in range(retries):

            try:

                response = client.models.embed_content(
                    model="gemini-embedding-001",
                    contents=text,
                )

                return response.embeddings[0].values

            except ServerError:

                if attempt < retries - 1:
                    time.sleep(5)
                    continue

                raise RuntimeError("Gemini Embedding está indisponível no momento")

            except ClientError as e:

                raise RuntimeError(f"Erro na API Gemini Embedding: {str(e)}")

            except ValueError:

                raise ValueError("O conteúdo enviado para embedding é inválido")

            except Exception as e:

                raise RuntimeError(f"Embedding generation failed: {str(e)}")
