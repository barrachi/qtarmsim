with import <nixpkgs> {};

mkShell {
  buildInputs = [
    python310
    uv
    boxes
  ];
}
