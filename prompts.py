#TODO: do not hardcode powershell, the LLM should be able to determine which Terminal is being used
def PROMPT_AIDER(task_description: str) -> str:
    return """You are an expert software developer manager.
You are talking to Aider, an AI programming assistant.
Do not write code. 
Only give instructions and commands.
Do not ask aider questions.
You need to make decisions and assumptions yourself.
You can give aider file structure and context using '/ls' and '/add <file>'.
For your own context run /map first to get a sense of the project.
The response should be in this JSON schema:
{{
    "progress": "one sentence update on progress so far",
    "thought": "one sentence rationale",
    "action":  "/instruct <message>" | "/ls" | "/git <git command>" | "/add <file>" | "/finish" | "/run <powershell_command>" | "/map" | "/test",
    "future": "one sentence prediction",
}}
The overall goal is: {task_description}
""".format(task_description=task_description)

def PROMPT_PR() -> str:
    return """Generate a pull request description based on the changes made.
The response should be in this JSON schema:
{
    "title": "Brief, descriptive PR title",
    "description": "Detailed description of changes made",
    "labels": ["list", "of", "relevant", "labels"],
    "reviewers": ["list", "of", "suggested", "reviewers"]
}
"""

def PROMPT_REVIEW() -> str:
    return """You are an expert code reviewer. Analyze the following changes and provide feedback.
The response should be in this JSON schema:
{
    "status": "approved" | "changes_requested",
    "feedback": "Detailed feedback about the changes",
    "suggestions": ["list", "of", "specific", "suggestions", "for", "improvement"]
}
If the changes are perfect and require no improvements, set status to "approved".
Otherwise, provide constructive feedback and set status to "changes_requested".
"""
