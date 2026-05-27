class InsightChunker:

    @staticmethod
    def generate(structured_document):
        """
        GENERATE ANALYTICAL CHUNKS.

        THIS CHUNK IS USED FOR:
        - PEDAGOGICAL INSIGHTS
        - EDUCATIONAL ANALYTICS
        - DASHBOARDS
        - PERFORMANCE ANALYSIS
        """

        content = f"""
Subject:
{structured_document.subject}

Level:
{structured_document.level}

Contents:
{'\n'.join(structured_document.contents)}

Skills Count:
{len(structured_document.skills)}

Methodologies Count:
{len(structured_document.methodologies)}

Assessment Count:
{len(structured_document.assessment)}
"""

        return [
            {
                "chunk_type": "insights",
                "content": content.strip(),
                "chunk_metadata": {
                    "subject": structured_document.subject,
                    "level": structured_document.level,
                    "document_id": structured_document.document_id,
                },
            }
        ]
