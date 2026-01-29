# Create Python Scripts Release

## Create Virtual Environment (venv)

### Create Windows venv

```bash
  python -m venv env
```

### Create MacOS/Linux venv

```bash
  python3 -m venv env
```

## Launch local virtual environment

### Launch Windows venv

```bash
  .env\Scripts\activate.ps1
```

### Through Windows WSL (Linux)

```bash
  source .env/bin/activate
```

### Launch MacOS/Linux venv

```bash
  source venv/bin/activate
```

## Install Requirements

```bash
  pip install -r requirements.txt
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
