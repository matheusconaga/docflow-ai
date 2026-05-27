class RecommendationChunker:

    @staticmethod
    def generate(structured_document):
        """
        GENERATE CHUNKS FOR PEDAGOGICAL RECOMMENDATIONS.

        THIS CHUNK IS USED FOR:
        - TEACHING RECOMMENDATIONS
        - CLASS ADAPTATIONS
        - LEARNING SUPPORT
        """

        # Pre-format the skills list to keep the f-string clean
        formatted_skills = []
        for skill in structured_document.skills:
            if skill.get("code"):
                formatted_skills.append(f"{skill['code']} - {skill['description']}")
            else:
                formatted_skills.append(skill["description"])

        content = f"""
Skills:
{'\n'.join(formatted_skills)}

Methodologies:
{'\n'.join(structured_document.methodologies)}

Assessment:
{'\n'.join(structured_document.assessment)}
"""

        return [
            {
                "chunk_type": "pedagogical_recommendation",
                "content": content.strip(),
                "chunk_metadata": {
                    "subject": structured_document.subject,
                    "level": structured_document.level,
                    "document_id": structured_document.document_id,
                },
            }
        ]
