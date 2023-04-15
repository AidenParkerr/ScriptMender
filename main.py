import argparse
from pathlib import Path
from GPTRequester import GPTRequester

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fix a Python script that contains errors using GPT API. \
            Any errors that arise with the script are given to GPT and attempt to fix. \
            The result from GPT is stored in the file modified_script.py and changes are presented in a HTML file.")
    parser.add_argument(
        'script_file',
        help="The Python script that contains errors.")
    parser.add_argument(
        'openai_key_file',
        help="Text file containing your openai API key.")
    args = parser.parse_args()

    if not Path(args.script_file).exists():
        raise FileNotFoundError(
            f"The script file `{args.script_file}` is not found.")
    if not Path(args.openai_key_file).exists():
        raise FileNotFoundError(
            f"The key file `{args.openai_key_file}` is not found.")

    mender = GPTRequester(script=args.script_file, key=args.openai_key_file)
    mender.fix_script()