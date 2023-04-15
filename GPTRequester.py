import os
import sys
import openai
import subprocess
from functools import lru_cache

from pathlib import Path
from HTMLFileCreator import HTMLCreator


class GPTRequester:
    PROMPT_LIMIT = 100
    MAX_OUTPUT_TOKENS = 150
    TEMPERATURE = 0.7 # less random response

    def __init__(self, script, key):
        openai.api_key = open(key, 'r').read().strip("\n")
        self.tokens_used = 0
        self.save_dir = Path(os.getcwd()) / "generated_files"
        self.script = Path(script)
        if not self.save_dir.exists():
            self.save_dir.mkdir()
        if not self.script.exists():
            raise FileNotFoundError("The script provided does not exist.")

    @lru_cache(maxsize=None) # Cache responses
    def send_gpt_request(self, prompt):
        print("Sending Request to GPT..")
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=self.TEMPERATURE
            )
            # check if reponse has "stop" flag indicating message was fully
            # sent or stopped due to tokens
            return self.handle_gpt_response(response)
        except openai.error.RateLimitError as e:
            print(f"Error Thrown from GPT:\n{e}")
            return None

    def handle_gpt_response(self, response):
        response_message = response.choices[0].message.content
        print("GPT Response:")
        print('-' * 40)
        print(response_message)
        print('-' * 40)
        return response_message

    def create_gpt_prompt(self, error, script_contents):
        with open("gpt_prompt.txt", 'r') as f:
            prompt = f.read()
        injected_prompt = prompt.format(error=error, code=script_contents)
        return injected_prompt
    
    def truncate_prompt(self, prompt):
        encoded_prompt = openai.api.encode(prompt)
        if len(encoded_prompt) > self.PROMPT_LIMIT:
            encoded_prompt = encoded_prompt[:self.PROMPT_LIMIT]
            truncated_prompt = openai.api.decode(encoded_prompt)
            return truncated_prompt
        return prompt

    def read_script(self, script):
        with open(script, 'r', encoding='utf-8') as f:
            content = f.read()
        return content

    def run_process(self, command):
        try:
            subprocess.run(
                command,
                text=True,
                check=True,
                capture_output=True,
                encoding="utf-8")
            return None
        except subprocess.CalledProcessError as e:
            return e.stderr

    def get_exact_error(self, output):
        return output.strip().split("\n")[-1]

    def save_modified_script(self, response, script):
        script_path = self.save_dir / script
        if script_path.exists():
            text = input(
                f"The file `{script_path}` already exists.\nOverwrite? Y/n: ")
            if text.lower() != 'y':
                print("File not overwritten.")
                return False

        with open(script_path, "w") as f:
            f.write(response)
        print(f"`{script_path}` Saved.")
        return True

    def format_to_pep8(self, script):
        command = [
            "autopep8",
            "--in-place",
            "--aggressive",
            "--aggressive",
            script]
        self.run_process(command)

    def fix_script(self):
        command = ["python", self.script]
        error = self.run_process(command)

        if not error:
            print("Script ran successfully. No errors found.")
            sys.exit(0)
        
        script_contents = self.read_script(self.script)
        exact_error = self.get_exact_error(error)
        prompt = self.create_gpt_prompt(
            error=exact_error, script_contents=script_contents)
        response = self.send_gpt_request(prompt)
        modified_script_path = self.save_dir / \
            f"UPDATED_{Path(self.script).stem}.py"
        if not self.save_modified_script(response, modified_script_path):
            # If file was not saved or user chose not to overwrite.
            print("See GPT response above for necessary code fix.")
            sys.exit(1)

        # Format to PEP8
        self.format_to_pep8(modified_script_path)
        modified_script = self.read_script(modified_script_path)
        if modified_script is not None:
            html_creator = HTMLCreator(
                save_dir=self.save_dir,
                orig_script=script_contents,
                modified_script=modified_script)
            html_creator.create_html_file()
            print("Created HTML File.")

        sys.exit(0)
