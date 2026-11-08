@echo off
cd /d "%~dp0.."
chcp 866 >nul
echo === Пакет curl, глубина 1 ===
python src\main.py --package curl --repo http://archive.ubuntu.com/ubuntu/dists/noble/main/binary-amd64/Packages.gz --max-depth 1
echo === Пакет curl, глубина 2, фильтр libc ===
python src\main.py --package curl --repo http://archive.ubuntu.com/ubuntu/dists/noble/main/binary-amd64/Packages.gz --max-depth 2 --filter libc
pause
