class AssessmentChunker:

    @staticmethod
    def generate(structured_document):
        """
        GENERATE CHUNKS FOR ASSESSMENT CREATION.

        THIS CHUNK IS USED FOR:
        - TEST GENERATION
        - QUIZZES
        - EVALUATION CREATION
        """

        # Pre-format the skills list to keep the f-string clean
        formatted_skills = []
        for skill in structured_document.skills:
            if skill.get("code"):
                formatted_skills.append(f"{skill['code']} - {skill['description']}")
            else:
                formatted_skills.append(skill["description"])

        content = f"""
Contents:
{'\n'.join(structured_document.contents)}

Skills:
{'\n'.join(formatted_skills)}

Assessment:
{'\n'.join(structured_document.assessment)}
"""

        return [
            {
                "chunk_type": "assessment_generation",
                "content": content.strip(),
                "chunk_metadata": {
                    "subject": structured_document.subject,
                    "level": structured_document.level,
                    "document_id": structured_document.document_id,
                },
            }
        ]
