@echo off
cd /d "%~dp0.."
chcp 866 >nul
echo === 1. Ромб ===
python src\main.py --repo-mode test --package A --repo examples\diamond.txt --ascii-tree --no-show
echo === 2. Цикл ===
python src\main.py --repo-mode test --package A --repo examples\cycle.txt --ascii-tree --no-show
echo === 3. Широкое дерево, глубина 2 ===
python src\main.py --repo-mode test --package A --repo examples\wide.txt --max-depth 2 --ascii-tree --no-show
echo === 4. Широкое дерево, фильтр H ===
python src\main.py --repo-mode test --package A --repo examples\wide.txt --filter H --ascii-tree --no-show
echo === 5. Большой граф: повторяющиеся поддеревья ===
python src\main.py --repo-mode test --package A --repo examples\big.txt --max-depth 10 --ascii-tree --no-show
pause
