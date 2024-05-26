# Grade planner for Dead By Daylight

This is a tool that let you create plans for upgrading grades in Dead By 
Daylight like this:

![demo.png](demos/demo.png)

## Main concept

Main goal of this tool is let to create something like a calendarfor upgrading 
grade step by step (yes, it becomes easier after recent update that not stole 
pips, but first version of this tool was created too far before this).

Each day in calendar is mark some grade: ash, bronze, silver etc. This mark 
means that you can live in this day with current grade or higher (you can get
bronze in 15th day from demo for example), but if your grade is lower, than 
you need to hurry up.

Days with same grades is called period. Each next period is longer by 1 day, 
except last that could be longer by 1-4 days because these days cannot be 
included in previous periods evenly, so it lets more days to relax or give 
reserve days to upgrade to last grade.

Whole plan starts and ends between 13th days of two close months (like in Dead 
By Daylight). Usually first period (ash) always contain 4 days, except every
February-March that contains 3 days.

Base logic of this tool creates for future customization, so you can customize
your plans more easily in future!

## Installing

Next instructions help you to install this standalone tool.

### Windows

1. Download code of this repository: click "Code" -> "Download ZIP", unpack it
anywhere
2. Install [Python 3.12](https://www.python.org/downloads/) or higher. On 
first step of installation, set checkbox "**Add python.exe to PATH**".
3. Double-click on `install_windows.bat` file.

Instead of last step, you can install all dependencies manually:

1. Open console in project directory and use next commands to create virtual 
environment, then activate it:

   ```commandline
    python -m venv .venv
    .venv\Scripts\activate.bat
    ```

2. Install dependencies. You can do it basically via `pip`:

    ```commandline
    pip install -r requirements.txt
    ```
   
   Or using `uv` which install dependencies faster:
    ```commandline
    pip install uv
    uv pip install -r requirements.txt
    ```

### Linux

First of all - download code of this repository one of two options:
   
1. Using `git clone`:
   
   ```commandline
   sudo apt install git
   cd /where/you/want/to/install
   git clone https://github.com/Holography7/DBDPlanner.git
   ```
   
2. Click "Code" -> "Download ZIP", unpack it anywhere.

After this the easiest way is run command `./install_linux.sh`, that creates 
virtual environment and install all dependencies. Remember that internet 
connection is required. You can skip next instructions if you run this command.

Manual installing dependencies:

1. Make sure that you have installed Python 3.12 or higher:

   ```commandline
   python --version
   ```

   If it's not (or you don't have python), then you should add repository that 
   contains all versions of Python and install 3.12. For example, for Ubuntu, 
   you can add deadsnakes repo and install Python 3.12 from it:

   ```commandline
   sudo add-apt-repository ppa:deadsnakes/ppa
   sudo apt update
   sudo apt install python3.12
   ```

   And then you should use command `python3.12` instead just `python`!

2. Open terminal (or just move with `cd`) in directory with project and use 
next commands to create virtual environment, then activate it:

    ```commandline
    python -m venv .venv
    source .venv/bin/activate
    ```

3. Install dependencies. You can do it basically via `pip`:

    ```commandline
    pip install -r requirements.txt
    ```
   
   Or using `uv` which install dependencies faster:
    ```commandline
    pip install uv
    uv pip install -r requirments.txt
    ```


### MacOS

There is no instructions for MacOS yet, but it could be very similar for Linux 
instruction, except Python 3.12 installation, where you should 
[download](https://www.python.org/downloads/) installer and install it like in 
Windows.

## Usage

**Important**: before usage of this project, you must activate virtual 
environment any time when you open terminal/console:

```commandline
.venv\Scripts\activate.bat  # Windows
source .venv/bin/activate  # Linux and MacOS
```

After this commands your terminal/console will start with `(.venv)` that means 
you activate virtual environment. Project works with only activated virtual 
environment!

Usage is pretty easy - just use next command to generate your plan on current
month:

```commandline
python create_plan.py
```

After some time you got message, that your plan was generated. All your plans
will store in `plans` directory.

For advanced usage you can generate plan on any other date. To do this, you
can use `-d` parameter and type date in ISO format between 13th days of two
months. For example, to make plan on May-June 2024, use this command:

```commandline
python create_plan.py -d 2024-05-13
```

Remember that type day before 13th day of any month, you get plan that starts 
in previous month. For example, date `2024-05-12` will creates plan on 
April-May 2024, not May-June!

## Developing

This project contains requirements for developing (usual users not need them 
to install). To install them, use one of this command:

```commandline
pip install -r dev_tools.txt
uv pip install -r dev_tools.txt
```

It contains `ruff` linter and formatter, `mypy` type checker and `pre-commit` 
hook. You can install pre-commit hook to run `ruff` and `mypy` every time
before commit:

```commandline
pre-commit install
```

Or, run them manually:
```commandline
ruff check
ruff format
mypy .
```

## Testing

Project contains `test.py` script for running manual tests to generate some
parts of images. Use command `python test.py --help` to get information about 
available tests. You can also use `--help` after every available test to see
options. All test results stores in `src/tests/manual_test_results`. Also you 
can see what this tests do in `src/tests/manual.py`.

Auto tests will come someday...

## Roadmap

- [ ] Testing on Windows and MacOS
- [ ] Add settings
- [ ] Add auto tests
- [ ] Add updating
- [ ] Add setup scripts
- [ ] Maybe add docker version?
- [ ] Add customization of mark
- [ ] GUI
