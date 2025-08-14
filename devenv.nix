{ pkgs, lib, config, ... }: {
  packages = [ pkgs.zlib ];
  languages.python = {
    enable = true;
    uv.enable = true;
  };
}
