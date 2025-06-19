#!/usr/bin/env python3

import datetime
import glob
import os
import subprocess
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class AssetsGenerator():
    PROJECT_NAME = 'qtarmsim'

    def __init__(self, version='0.0.0+unknown'):
        self.project_root = Path(__file__).parent.parent
        self.src_dir = os.path.join(self.project_root, 'src', self.PROJECT_NAME)
        self.version = version

    def compile_ui_files(self):
        """Compiles all .ui files to ui_*.py files."""
        print("Compiling .ui files...")
        ui_files = glob.glob(os.path.join(self.src_dir, 'ui', '*.ui'))
        for ui_file in ui_files:
            output_file = os.path.join(self.src_dir, 'ui', f"ui_{Path(ui_file).name.replace('.ui', '.py')}")
            print(f"  - Compiling {ui_file} to {output_file}")
            subprocess.run(['pyside6-uic', ui_file, '-o', str(output_file)], check=True)
        print("Finished compiling .ui files.")

    def compile_qrc_files(self):
        """Compiles all .qrc files to *_rc.py files."""
        print("Compiling .qrc files...")
        qrc_files = glob.glob(os.path.join(self.src_dir, 'res', '*.qrc'))
        for qrc_file in qrc_files:
            output_file = os.path.join(self.src_dir, 'res', f"{Path(qrc_file).name.replace('.qrc', '_rc.py')}")
            print(f"  - Compiling {qrc_file} to {output_file}")
            subprocess.run(['pyside6-rcc', qrc_file, '-o', str(output_file)], check=True)
        print("Finished compiling .qrc files.")

    def update_files_from_templates(self):
        in_files = [os.path.join(self.src_dir, 'res', 'desktop', 'qtarmsim.appdata.xml.in'), ]
        for in_file in in_files:
            out_file = in_file[:-3]
            print("Updating {}...".format(out_file))
            with open(in_file, encoding="utf-8") as f:
                text = f.read()
            text = text \
                .replace("@MARKER@", "") \
                .replace("@VERSION@", self.version) \
                .replace("@DATE@", datetime.date.today().isoformat())
            with open(out_file, 'w', encoding="utf-8") as f:
                f.write(text)

    def do_all(self):
        self.compile_ui_files()
        self.compile_qrc_files()
        self.update_files_from_templates()


class CustomBuildHook(BuildHookInterface):
    PLUGIN_NAME = 'custom'  # This matches the hook name in pyproject.toml

    def initialize(self, version: str, build_data: dict) -> None:
        """
        Runs before each build target (sdist, wheel).
        This is where you'd generate files that go *into* your package.
        """
        if self.target_name == 'sdist':
            ag = AssetsGenerator(self.metadata.version)
            ag.do_all()

    def finalize(self, version: str, build_data: dict, artifact) -> None:
        """
        Runs after each build target (sdist, wheel).
        """
        pass


if __name__ == "__main__":
    # Only for debugging purposes, 'uv build' should be used to properly execute this file
    ag = AssetsGenerator()
    ag.compile_ui_files()
    ag.compile_qrc_files()
    ag.update_files_from_templates()
