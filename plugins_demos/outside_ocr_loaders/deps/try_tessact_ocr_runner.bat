@echo off
if not defined venv_path (
    set venv_path=D:\ProgramData\Miniconda3\envs\snap_test2\
)

if not defined tesseract_path (
    set tesseract_path=D:\GreenSoftware\Tesseract-OCR
)

set path=%venv_path%;%venv_path%\Scripts;%tesseract_path%;%path%

python %~dp0tessact_ocr_runner.py --input_path=%1 --output_path=%2