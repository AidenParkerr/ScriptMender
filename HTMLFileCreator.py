import os
import html
import difflib
from pathlib import Path


class HTMLCreator():
    def __init__(self, save_dir, orig_script, modified_script) -> None:
        self.save_dir: Path = Path(save_dir)
        self.orig_script = orig_script
        self.modified_script = modified_script
        self.html_template = self.get_html_template()

        if not self.save_dir.exists():
            self.save_dir.mkdir()

    def check_differences(self):
        "https://docs.python.org/3/library/difflib.html#differ-objects"
        d = difflib.Differ()
        differences = list(
            d.compare(
                self.orig_script.splitlines(),
                self.modified_script.splitlines()))
        # remove leading white space from first
        differences[0] = differences[0].lstrip()
        content = ''
        for line in differences:
            if line.startswith('-'):
                content += self.write_coloured_text(line, "red")
            elif line.startswith('+'):
                content += self.write_coloured_text(line, "green")
            elif line.startswith('?') or line.isspace():
                continue
            else:
                content += self.write_coloured_text(line, "black")
        return content

    def write_coloured_text(self, text, colour):
        return f'<span style="color:{colour};">{html.escape(text)}</span><br>'

    def get_html_template(self):
        html_path = Path(os.getcwd()) / "html_template.html"
        with open(html_path, 'r') as f:
            return f.read()

    def create_html_file(self):
        formatted_html = self.html_template.format(
            differences=self.check_differences(),
            orig_script=self.orig_script,
            modified_script=self.modified_script
        )
        with open(self.save_dir / "Changes_Made_to_Script.html", "w") as f:
            f.write(formatted_html)
