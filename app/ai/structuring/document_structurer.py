import json
import time

from google import genai
from google.genai.errors import ServerError

from app.core.config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)


class DocumentStructurer:

    @staticmethod
    def structure(extracted_text: str):

        prompt = f"""
Você é especialista em documentos pedagógicos brasileiros.

REGRAS:
- Responda APENAS JSON válido
- Não utilize markdown
- Todos os campos devem estar em português
- Corrija pequenos erros de OCR
- Preserve códigos BNCC/habilidades quando existirem

Formato:

{{
  "subject": "",
  "level": "",
  "contents": [],
  "skills": [
    {{
      "code": "",
      "description": ""
    }}
  ],
  "methodologies": [],
  "assessment": []
}}

REGRAS PARA skills:
- Preserve códigos como EF01ER05
- "code" = código BNCC sem parênteses
- Se não existir código, use null
- "description" = descrição completa da habilidade
- Não resuma habilidades

DOCUMENTO:
{extracted_text}
"""

        retries = 3

        for attempt in range(retries):

            try:

                response = client.models.generate_content(
                    model="gemini-2.5-flash", contents=prompt
                )

                clean_text = (
                    response.text.replace("```json", "").replace("```", "").strip()
                )

                return json.loads(clean_text)

            except ServerError:

                if attempt < retries - 1:
                    time.sleep(5)
                    continue

                raise RuntimeError("Gemini está indisponível no momento")

            except json.JSONDecodeError:

                raise ValueError("A IA retornou JSON inválido")

            except Exception as e:

                raise RuntimeError(str(e))
