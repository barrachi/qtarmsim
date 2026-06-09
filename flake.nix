{
  description = "QtARMSim – Easy to use graphical ARM simulator";

  inputs = {
    nixpkgs.url     = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";

    # PySide6 >= 6.10 bundled Qt links against libtiff.so.5, but current
    # nixpkgs ships libtiff.so.6.  Pin an older nixpkgs for libtiff5.
    # Only needed for the devShell (bundled-Qt wheel from PyPI); the nix
    # run package uses nixpkgs' own PySide6 which links against its own libtiff.
    nixpkgs-tiff5 = {
      url   = "github:NixOS/nixpkgs/c140343a04fd6b9aab86a5cc2656fa0acf1a2a01";
      flake = false;
    };
  };

  outputs = { self, nixpkgs, flake-utils, nixpkgs-tiff5 }:
    flake-utils.lib.eachSystem [ "x86_64-linux" "aarch64-linux" ] (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        # libtiff.so.5 from the pinned nixpkgs revision
        libtiff5 = (import nixpkgs-tiff5 { inherit system; }).libtiff;

        # ── System libraries required by PySide6's bundled Qt (devShell) ──
        # Derived from nix-env/qtarmsim-fhs.nix.
        pyside6SystemLibs = with pkgs; [
          stdenv.cc.cc.lib
          alsa-lib
          at-spi2-atk
          brotli              # PySide6 >= 6.10.0
          bzip2
          cacert
          cairo
          cups
          dbus
          expat
          fontconfig
          freetype
          gdk-pixbuf
          glib
          gtk3
          harfbuzz
          libcap
          libdrm
          libGL
          libglvnd
          libkrb5
          libpulseaudio
          libpng
          libtiff5            # PySide6 >= 6.10.0 (from pinned nixpkgs)
          libxau
          libxcb-cursor
          libxcb-util
          libxdmcp
          libxkbcommon
          nspr
          nss
          pango
          pcre2
          pcsclite
          udev
          vulkan-loader       # PySide6 >= 6.10.0
          wayland
          xz
          zlib
          zstd
          inetutils           # telnet – handy for armsim connection debugging
        ] ++ (with pkgs.xorg; [
          libX11
          libxcb
          libXcomposite
          libXcursor
          libXdamage
          libXext
          libXfixes
          libXi
          libxkbfile
          libXrandr
          libXrender
          libxshmfence
          libXtst
          setxkbmap
          xcbutilimage
          xcbutilkeysyms
          xcbutilrenderutil
          xcbutilwm
          xf86inputevdev
        ]);

        # Qt environment tweaks needed when running PySide6's bundled Qt
        bundledQtProfile = ''
          unset QT_PLUGIN_PATH
          unset QTWEBKIT_PLUGIN_PATH
          unset QML2_IMPORT_PATH
          export QML_DISABLE_DISK_CACHE=1
        '';

        # ── nix run / nix build ────────────────────────────────────────────
        # Uses nixpkgs' own Python + PySide6 package.  nixpkgs handles Qt
        # linkage via Nix store RPATHs so no FHSenv wrapper is required here.
        #
        # Notes:
        #   • pyproject.toml pins pyside6==6.10.2; nixpkgs ships a newer
        #     version which is API-compatible.  The pin is not enforced by the
        #     nixpkgs build system.
        #   • hatch-vcs reads the git tree to determine the version.  The Nix
        #     sandbox has no .git, so we supply a fixed version via the env var
        #     that hatch-vcs/setuptools-scm respects.
        #   • The generate_assets build hook calls pyside6-uic and pyside6-rcc;
        #     adding pyside6 to nativeBuildInputs puts those tools on PATH.
        qtarmsim = pkgs.python3Packages.buildPythonApplication {
          pname   = "qtarmsim";
          version = "2.0.0rc";
          src     = self;
          pyproject = true;

          build-system = with pkgs.python3Packages; [
            hatchling
            hatch-vcs
            hatch-fancy-pypi-readme
          ];

          nativeBuildInputs = [
            pkgs.qt6.qtbase   # provides libexec/uic and libexec/rcc
          ];

          # We only use qtbase for its build tools (uic/rcc); PySide6 handles
          # its own Qt environment at runtime, so nixpkgs' Qt app wrapping is not needed.
          dontWrapQtApps = true;

          # The generate_assets build hook only runs for sdist targets, not
          # wheel targets.  The generated *_rc.py / ui_*.py files are gitignored,
          # so they are absent from the flake's `self` source.  Generate them
          # here before hatchling builds the wheel.
          preBuild = let
            # Qt6's uic/rcc live in libexec/ and support '-g python' natively,
            # so we can use them directly without a PySide6 Python environment.
            qtbase = pkgs.qt6.qtbase;
          in ''
            echo "Compiling .ui files..."
            for ui in src/qtarmsim/ui/*.ui; do
              name=$(basename "$ui" .ui)
              ${qtbase}/libexec/uic -g python "$ui" -o "src/qtarmsim/ui/ui_$name.py"
            done
            echo "Compiling .qrc files..."
            for qrc in src/qtarmsim/res/*.qrc; do
              name=$(basename "$qrc" .qrc)
              ${qtbase}/libexec/rcc -g python "$qrc" -o "src/qtarmsim/res/''${name}_rc.py"
            done
          '';

          dependencies = with pkgs.python3Packages; [
            pyside6
            typing-extensions
          ];

          env.SETUPTOOLS_SCM_PRETEND_VERSION = "2.0.0rc";

          meta = with pkgs.lib; {
            description = "Easy to use graphical ARM simulator";
            homepage    = "https://lorca.act.uji.es/project/qtarmsim/";
            license     = licenses.gpl3Plus;
            mainProgram = "qtarmsim";
            platforms   = platforms.linux;
          };
        };

      in {
        # ── nix run / nix build ────────────────────────────────────────────
        packages.default = qtarmsim;

        # ── nix develop ───────────────────────────────────────────────────
        # FHSenv satisfies the system-library requirements of PySide6's
        # bundled Qt wheel (installed by uv into a project-local .venv).
        #
        # First-time setup inside the shell:
        #   uv venv --python 3.12
        #   uv pip install -e . hatchling ruff basedpyright typing_extensions
        #
        # Then to run the development version:
        #   uv run qtarmsim
        devShells.default = (pkgs.buildFHSEnv {
          name = "qtarmsim-dev";

          targetPkgs = _: pyside6SystemLibs ++ (with pkgs; [
            # Python runtime targeted by the .venv
            python312

            # Package / virtual-env manager
            uv

            # Development tools
            git
            basedpyright
            ruff
            rstfmt
            boxes

            # Build toolchain (needed when uv compiles native wheels)
            gcc
            bintools
            pkg-config
            cacert
          ]);

          profile = bundledQtProfile + ''
            # Project's .venv takes priority over system Python
            export PATH=".venv/bin:$PATH"
            # Tell uv to prefer the Python provided by this FHS env
            export UV_PYTHON_PREFERENCE=only-system
            # SSL certificates for uv downloads
            export SSL_CERT_FILE="${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"
            export NIX_SSL_CERT_FILE="${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"
          '';

          runScript = "bash";
        }).env;
      }
    );
}
