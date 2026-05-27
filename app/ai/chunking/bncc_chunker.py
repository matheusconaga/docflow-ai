class BNCCChunker:

    @staticmethod
    def generate(structured_document):
        """
        GENERATE BNCC-FOCUSED CHUNKS.

        THIS CHUNK IS USED FOR:
        - BNCC ALIGNMENT
        - CURRICULUM VALIDATION
        - PEDAGOGICAL COMPLIANCE
        """

        chunks = []

        for skill in structured_document.skills:

            content = f"""
BNCC Skill:
{skill.get("code", "NO_CODE")}

Description:
{skill["description"]}
"""

            chunks.append(
                {
                    "chunk_type": "bncc_alignment",
                    "content": content.strip(),
                    "chunk_metadata": {
                        "subject": structured_document.subject,
                        "level": structured_document.level,
                        "document_id": structured_document.document_id,
                        "skill_code": skill.get("code"),
                    },
                }
            )

        return chunks
