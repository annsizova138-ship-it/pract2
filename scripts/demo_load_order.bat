@echo off
cd /d "%~dp0.."
chcp 866 >nul
echo === 1. Цепочка ===
python src\main.py --repo-mode test --package A --repo examples\chain.txt --max-depth 10 --load-order
echo === 2. Ромб: D раньше B и C ===
python src\main.py --repo-mode test --package A --repo examples\diamond.txt --max-depth 10 --load-order
echo === 3. Цепочка, глубина 2 ===
python src\main.py --repo-mode test --package A --repo examples\chain.txt --max-depth 2 --load-order
echo === 4. Ромб, фильтр D ===
python src\main.py --repo-mode test --package A --repo examples\diamond.txt --filter D --load-order
echo === 5. Цикл ===
python src\main.py --repo-mode test --package A --repo examples\cycle.txt --max-depth 10 --load-order
echo === 6. Большой граф ===
python src\main.py --repo-mode test --package A --repo examples\big.txt --max-depth 10 --load-order
pause
