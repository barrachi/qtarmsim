with import <nixpkgs> {};

mkShell {
  buildInputs = [
    python311
    python311Packages.sphinx
    python311Packages.doc8   # linter
    rstfmt
    jetbrains.pycharm-professional
    boxes
    uv
  ];
}
