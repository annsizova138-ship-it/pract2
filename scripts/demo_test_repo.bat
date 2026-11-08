@echo off
cd /d "%~dp0.."
chcp 866 >nul
echo === 1. Цепочка, полный граф ===
python src\main.py --repo-mode test --package A --repo examples\chain.txt --max-depth 10
echo === 2. Цепочка, глубина 2 ===
python src\main.py --repo-mode test --package A --repo examples\chain.txt --max-depth 2
echo === 3. Ромб: общий пакет один раз ===
python src\main.py --repo-mode test --package A --repo examples\diamond.txt --max-depth 10
echo === 4. Широкое дерево, глубина 1 ===
python src\main.py --repo-mode test --package A --repo examples\wide.txt --max-depth 1
echo === 5. Широкое дерево, фильтр H ===
python src\main.py --repo-mode test --package A --repo examples\wide.txt --max-depth 10 --filter H
echo === 6. Цикл ===
python src\main.py --repo-mode test --package A --repo examples\cycle.txt --max-depth 10
echo === 7. Пакет зависит сам от себя ===
python src\main.py --repo-mode test --package A --repo examples\self.txt
echo === 8. Большой граф, пакет B ===
python src\main.py --repo-mode test --package B --repo examples\big.txt --max-depth 10
echo === 9. Ошибка: неизвестный пакет ===
python src\main.py --repo-mode test --package Z --repo examples\big.txt
echo === 10. Ошибка: корневой пакет исключён фильтром ===
python src\main.py --repo-mode test --package A --repo examples\big.txt --filter A
pause
