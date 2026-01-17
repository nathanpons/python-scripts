# Create Python Scripts Release

## Launch local virtual environment

```bash
  .env\Scripts\activate.ps1
```

## Build App Artifact

```bash
  pyinstaller PythonScripts.spec
```

The newly created artifact can be found at `dist/PythonScripts.exe`

## Releasing

Open the `Releases` section of GitHub and create a new release.

Create a tag for the release version and add a title labeled `Python Scripts v{VERSION_NUMBER}`.

Add the artifact to the binaries section at the bottom.
