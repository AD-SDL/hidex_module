# hidex_module

Contains `hidex_node`, providing an interface and adapter that works alongside the Hidex Plate Reader's first party driver to control the instrument.

## Building the C# Solution

To use this interface, you must first open `src/hidex_interface/HidexInterface.sln` and build the solution.

## Python Installation/Usage

This package is Windows-only.

### Using virtualenv

1. Open Command Prompt and navigate to the project directory.
2. Create a virtual environment:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   ```
   venv\Scripts\activate
   ```
4. Install the package and dependencies:
   ```
   pip install -r requirements.txt
   ```

### Using pdm

1. Install PDM if you don't have it: https://pdm-project.org/latest/#installation
2. Navigate to the project directory.
3. Install dependencies:
   ```
   pdm install
   ```
4. To start the node:
   ```
   pdm run python src/hidex_rest_node.py
   ```
