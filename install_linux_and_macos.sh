python_version="system"

# Parsing named arguments
while [ $# -gt 0 ]; do
  case "$1" in
    --python-version=*)
      python_version="${1#*=}"
      if ! [[ "$python_version" =~ 3\.1[23] ]]
      then
        printf "Invalid argument value of python-version: supported only 3.12 and 3.13 versions."
        exit 1
      fi
      ;;
    *)
      printf "Invalid argument: %s\n" "$1"
      exit 1
      ;;
  esac
  shift
done
if [ "$python_version" == "system" ]
then
  echo "Installation script will use system python"
else
  echo "Installation script will use python $python_version"
fi

# Check installed python
echo "Performing preinstallation checks..."
if [ "$python_version" == "system" ]
then
  # If user not selected python version with "--python-version" then using system python
  python_command="python"
  if ! command -v "$python_command" &> /dev/null
  then
    echo "Python command could not be found. Probably, you need to install Python 3.12 or higher in your system."
    exit 1
  fi

  installed_python_version=$(python -V 2>&1 | grep -Po '(?<=Python )(.+)')
  if ! [[ "$installed_python_version" =~ 3\.1[23].* ]]
  then
    echo "Your installed Python is outdated ($(python -V)) for this project. Install Python 3.12 or higher."
    exit 1
  else
    echo "Detected system python $installed_python_version"
  fi
else
  # If user not selected python version with "--python-version" then just check that this version just exists
  python_command="python$python_version"
  if ! command -v "$python_command" &> /dev/null
  then
    echo "Python $python_version not found. Probably, you need to install it in your system."
    exit 1
  fi
  echo "Detected python $python_version"
fi

# Create virtual environment
if [ -d ".venv" ]; then
  echo "Virtual environment already exist."
else
  echo "Virtual environment does not exists. Creating..."
  $python_command -m venv .venv
fi

# Install dependencies from requirements.txt
echo "Activating virtual environment..."
source .venv/bin/activate
echo "Installing uv..."
pip install uv
echo "Installing others requirements..."
uv pip install -r requirements.txt
echo "Installation complete!"
