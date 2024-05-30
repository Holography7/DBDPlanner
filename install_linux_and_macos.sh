echo "Performing preinstallation checks..."
if ! command -v python &> /dev/null
then
  echo "Python command could not be found. Probably, you need to install Python 3.12 or higher in your system."
  exit 1
fi

if [ "$(python -c 'import sys; major, minor = sys.version_info[0:2]; print(major == 3 and minor >= 12)')" == "False" ]
then
  echo "$(python -V) is installed as system Python, that outdated for this project. Trying to find not system python 3.12..."
  if ! command -v python3.12 &> /dev/null
  then
    echo "Your installed Python is outdated ($(python -V)) for this project. Install Python 3.12 or higher."
    exit 1
  else
    echo "Founded!"
    python_command="python3.12"
  fi
else
  python_command="python"
fi

if [ -d ".venv" ]; then
  echo "Virtual environment already exist."
else
  echo "Virtual environment does not exists. Creating..."
  $python_command -m venv .venv
fi

echo "Activating virtual environment..."
source .venv/bin/activate
echo "Installing uv..."
pip install uv
echo "Installing others requirements..."
uv pip install -r requirements.txt
echo "Installation complete!"
