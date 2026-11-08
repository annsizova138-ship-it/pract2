@echo off
cd /d "%~dp0.."
chcp 866 >nul
echo === Пакет nano ===
python src\main.py --package nano --repo http://archive.ubuntu.com/ubuntu/dists/noble/main/binary-amd64/Packages.gz --max-depth 20 --load-order
echo === Пакет wget ===
python src\main.py --package wget --repo http://archive.ubuntu.com/ubuntu/dists/noble/main/binary-amd64/Packages.gz --max-depth 20 --load-order
echo === Пакет curl ===
python src\main.py --package curl --repo http://archive.ubuntu.com/ubuntu/dists/noble/main/binary-amd64/Packages.gz --max-depth 20 --load-order
pause
