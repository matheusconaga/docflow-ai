class ActivityChunker:

    @staticmethod
    def generate(structured_document):
        """
        GENERATE CHUNKS FOR ACTIVITY GENERATION.

        THIS CHUNK IS USED FOR:
        - EXERCISES
        - CLASSROOM ACTIVITIES
        - HOMEWORK GENERATION
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

Methodologies:
{'\n'.join(structured_document.methodologies)}
"""

        return [
            {
                "chunk_type": "activity_generation",
                "content": content.strip(),
                "chunk_metadata": {
                    "subject": structured_document.subject,
                    "level": structured_document.level,
                    "document_id": structured_document.document_id,
                },
            }
        ]
