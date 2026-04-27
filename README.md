# Squarespace to Wix Blog Convertor

**_A Python script for preparing a SquareSpace blog export for import to Wix._**

---
## What it does


---

## How to use

### Export from Squarespace
- TODO

### Use the Conversion Script
1. [Fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo) this repo and clone it locally.
2. _Recommended_: [Create a venv](https://www.w3schools.com/python/python_virtualenv.asp) (**v**irtual **env**ironment), activate it[^1], *then*:
3. Run `pip install -r requirements.txt`
4. Move your Squarespace XML file into this directory.
5. Configure the script settings by editing the global constants at the top of `convert.py`.
6. Run `python convert.py`.

### Import to Wix
- take the generated output file
- TODO

### Optional: Redirect SquareSpace Links

---

## How it works


General Notes
- I avoid using soup.prettify() because it appears to cause issues with Wix's ability to correctly parse the XML

[^1]: If you set up a [venv using VS Code](https://code.visualstudio.com/docs/python/python-tutorial#_create-a-virtual-environment) like I did, it can conveniently activate every time you open this project