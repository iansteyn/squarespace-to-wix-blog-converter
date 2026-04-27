# Squarespace to Wix Blog Convertor

**_A Python script for preparing a SquareSpace blog export for import to Wix._**

---
## What it does


---

## Usage

Get the Squarespace Export
- TODO

Set up the script
- fork this repo and/or clone it locally [link: how to]
- recommended: create a venv, [link to instructions], enter the venv, *then*:
- run `pip install -r requirements.txt`
- move your Squarespace XML file
- edit the configuration constants at the top of `convert.py`

Run the script
- run `python convert.py`

Upload to Wix
- take the generated output file
- TODO

---

## How it works


General Notes
- I avoid using soup.prettify() because it appears to cause issues with Wix's ability to correctly parse the XML
