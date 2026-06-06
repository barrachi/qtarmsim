# To find required depencies of PySide6
# find .venv/lib/python3.11/site-packages/PySide6/ -name "*.so" -exec ldd {} \; | grep not
#
# To debug possible failures (after nix-shell this file):
# set -x QT_DEBUG_PLUGINS 1; set -x QT_LOGGING_RULES  "qt.qpa.*=true"; uv run qtarmsim

{ pkgs ? import <nixpkgs> {} }:

let
  tiff5pkgs = import (builtins.fetchTarball {
    url = "https://github.com/NixOS/nixpkgs/archive/c140343a04fd6b9aab86a5cc2656fa0acf1a2a01.tar.gz";
  }) {};
  libtiff5 = tiff5pkgs.libtiff;

in
(pkgs.buildFHSEnv {
  name = "qtarmsim-fhs";
  targetPkgs = pkgs: (with pkgs;
      [
        stdenv.cc.cc.lib
        alsa-lib
        at-spi2-atk
        bintools
        brotli # PySide >=6.10.0 requirement
        bzip2
        cacert
        cairo
        ccache
        clang-tools
        cups
        dbus
        expat
        fontconfig
        freetype
        gcc
        gdb
        gdk-pixbuf
        git
        glib
        gnat14
        gtk3
        harfbuzz
        libcap
        libdrm
        libevdev
        libgbm
        libGL
        libglvnd
        # libglvnd.dev
        libkrb5
        libpulseaudio
        libpng
        libtiff5 # PySide >=6.10.0 requirement
        libxau
        libxcb-cursor
        # libxcb-cursor.dev
        libxcb-util
        libxdmcp
        libxkbcommon
        # libxkbcommon.dev
        nspr
        nss
        pango
        pcre2
        pcsclite
        pkg-config
        ruby
        udev
        vulkan-loader # PySide >=6.10.0 requirement
        wayland
        which
        # xcb-util-cursor
        # xcb-util-cursor-HEAD
        # xcb-util-cursor-HEAD.dev
        xz
        zlib
        zstd
        inetutils # telnet
      ]) ++ (with pkgs.xorg;
        [
          libX11
          # libX11.dev
          libxcb
          # libxcb.dev
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
  profile = ''
          unset QT_PLUGIN_PATH
          unset QTWEBKIT_PLUGIN_PATH
          unset QML2_IMPORT_PATH
          export QML_DISABLE_DISK_CACHE=1
          export PATH=${pkgs.ruby}/bin:.venv/bin:$PATH
      '';
  runScript = "fish --init-command='gem install --user-install shell sync e2mmap; source .venv/bin/activate.fish'";
}).env
