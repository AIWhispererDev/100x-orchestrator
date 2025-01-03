import os
from dotenv import load_dotenv

load_dotenv()
print(f'DEEPSEEK_API_KEY={os.getenv("DEEPSEEK_API_KEY", "Not found")}')
