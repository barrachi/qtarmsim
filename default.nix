with import <nixpkgs> {};

mkShell {
  buildInputs = [
    python312
    python312Packages.sphinx
    python312Packages.doc8   # linter
    ruff                     # Extremely fast Python linter and code formatter
    pyright                  # Type checker for the Python language
    rstfmt
    jetbrains.pycharm
    boxes
    uv
    claude-code
  ];
}
