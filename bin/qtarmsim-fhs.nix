{ pkgs ? import <nixpkgs> {} }:

(pkgs.buildFHSEnv {
  name = "qtarmsim-fhs";
  targetPkgs = pkgs: (with pkgs;
      [
      alsa-lib
      bintools
      bzip2
      cacert
      ccache
      clang-tools_14
      dbus
      expat
      fontconfig
      freetype
      gcc
      gdb
      git
      glib
      libdrm
      libevdev
      libGL
      libglvnd
      libglvnd.dev
      libkrb5
      libpulseaudio
      libxkbcommon
      libxkbcommon.dev
      nspr
      nss
      pkg-config
      ruby
      udev
      which
      xcb-util-cursor
      xz
      zlib
      zstd
    ]) ++ (with pkgs.xorg;
      [
        libX11
        libX11.dev
        libxcb
        libxcb.dev
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
