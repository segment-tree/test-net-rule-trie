{
  description = "A very basic flake";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };
  
  outputs = inputs @ {
    self,
    nixpkgs,
    flake-parts,
    ...
  } : flake-parts.lib.mkFlake { inherit inputs; } {
    flake = {
    };
    systems = [
      "x86_64-linux"
      "x86_64-darwin"
      "aarch64-linux"
      "aarch64-darwin"
    ];
    perSystem = { system, pkgs, ... }: let
      pkgs = import nixpkgs {
        inherit system;
      };
    in rec {
      packages.default = pkgs.stdenv.mkDerivation{
        name = "bubbles-valley";
        src = ./.;
        buildInputs = with pkgs; [
          which
          (python312.withPackages (ps: []))
        ];
        buildPhase = "";
        installPhase = ''
          name=bubbles-valley
          PYTHON=`which python`
          
          mkdir -p $out/bin/
          cp -r $src $out/src
          echo -e "#!/bin/sh\ncd $out/src; $PYTHON main.py" > $out/bin/$name
          chmod +x $out/bin/$name
        '';
      };
      devShells.default = pkgs.mkShell {
        packages = with pkgs; [ (python312.withPackages (ps: [ ps.numpy ps.datrie ps.marisa-trie])) ];
      };
    };
  };
}