cd /d "%~dp0"
call ".venv\Scripts\activate.bat"
python "src\hidex_rest_node.py" --node_url http://suestorm.cels.anl.gov:3000 --node_definition "C:\\Users\\RPL\\source\\repos\\hidex_module\\definitions\\hidex_howard.node.yaml"
pause
