# easy_pay_website
easy pay website

python3 -m pip install --upgrade build
python3 -m build

python3 -m pip install --upgrade twine
python3 -m twine upload --repository pypi dist/*
