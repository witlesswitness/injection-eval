import os
from anthropic import Anthropic
from dotenv import load_dotenv

TOOLS = [
    {
        "name": "read_file",
        "description": "Read the contents of a file by its path.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "The file path to read."},
            },
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Write (or overwrite) a file with the given text contents.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "The file path to write."},
                "content": {"type": "string", "description": "The text to write into the file."},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "list_files",
        "description": "List all file paths available in the workspace.",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
]

load_dotenv()
client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

resp = client.messages.create(
    model="claude-haiku-5-5",
    max_tokens=300,
    tools=TOOLS,
    messages=[{"role": "user", "content": "What files are available? Use your tools."}],
)
print("stop_reason:", resp.stop_reason)
for block in resp.content:
    print(block)