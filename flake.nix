{
  description = "PoC UNICONT: assistente de conformidade para os Núcleos de Controle Interno";

  inputs.nixpkgs.url = "github:nixos/nixpkgs/54170c54449ea4d6725efd30d719c5e505f1c10e";

  outputs =
    { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
      tesseractPortuguese = pkgs.tesseract.override { enableLanguages = [ "eng" "por" ]; };
      pythonPackages =
        python: with python; [
          anthropic
          fastapi
          jinja2
          pillow
          pydantic
          pymupdf
          python-multipart
          reportlab
          uvicorn
        ];
      developmentPackages =
        python: with python; [
          httpx
          playwright
          pytest
        ];
      python = pkgs.python312;
      unicontPoc = python.pkgs.buildPythonApplication {
        pname = "unicont-poc";
        version = "0.1.0";
        pyproject = true;
        src = ./.;
        build-system = [ python.pkgs.setuptools ];
        dependencies = pythonPackages python.pkgs;
        makeWrapperArgs = [
          "--prefix PATH : ${pkgs.lib.makeBinPath [ tesseractPortuguese ]}"
        ];
        doCheck = false;
      };
    in
    {
      packages.${system}.default = unicontPoc;

      apps.${system}.default = {
        type = "app";
        program = "${unicontPoc}/bin/unicont-poc-demo";
      };

      devShells.${system}.default = pkgs.mkShell {
        packages = [
          (python.withPackages (p: pythonPackages p ++ developmentPackages p))
          tesseractPortuguese
          pkgs.ffmpeg
        ];
        PLAYWRIGHT_BROWSERS_PATH = "${pkgs.playwright-driver.browsers}";
        PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS = "true";
        PYTHONPATH = "src";
      };
    };
}
