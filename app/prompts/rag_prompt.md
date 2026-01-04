You are assisting with a Retrieval-Augmented Generation task.

Given:
- Query: {{query}}
- Retrieved context:
{{context}}

Generate the final answer with these rules:
1. Prioritize retrieved context over prior knowledge.
2. If context does not contain the answer, explicitly state "context not sufficient".
3. Provide a clear, structured Markdown response.
