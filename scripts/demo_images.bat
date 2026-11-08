@echo off
cd /d "%~dp0.."
chcp 866 >nul
echo Закрывайте окно просмотра картинки, чтобы увидеть следующий граф
python src\main.py --repo-mode test --package A --repo examples\diamond.txt
python src\main.py --repo-mode test --package A --repo examples\cycle.txt
python src\main.py --repo-mode test --package A --repo examples\big.txt --max-depth 10
pause
