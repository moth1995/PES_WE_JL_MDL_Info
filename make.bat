@echo on
set PY_FILE=mdl_info.py
set PROJECT_NAME=mdl_info
set VERSION=1.0.0
set FILE_VERSION=file_version_info.txt 

pyinstaller --onefile "%PY_FILE%" --name "%PROJECT_NAME%_%VERSION%" --version-file "%FILE_VERSION%"

cd dist
tar -acvf "%PROJECT_NAME%_%VERSION%.zip" * config
pause
