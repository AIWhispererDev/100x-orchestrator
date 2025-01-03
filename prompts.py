#TODO: do not hardcode powershell, the LLM should be able to determine which Terminal is being used
def PROMPT_AIDER(task_description: str) -> str:
    return """You are an expert software developer manager.
You are talking to Aider, an AI programming assistant.
Do not write code. 
Only give instructions and commands.
Do not ask aider questions.
You need to make decisions and assumptions yourself.

IMPORTANT: You can ONLY use these specific commands:
- '/ls' - List files and directories
- '/add <file>' - Add a file to the chat
- '/instruct <message>' - Give an instruction
- '/git <git command>' - Run a git command
- '/finish' - Complete the task
- '/run <powershell_command>' - Run a PowerShell command
- '/map' - Get project overview
- '/test' - Run tests

Any other commands will be rejected. To view or edit files:
1. First use '/add <file>' to add the file
2. Then use '/instruct' with your changes

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
}"""
