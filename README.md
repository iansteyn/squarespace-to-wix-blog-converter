# Squarespace to Wix Blog Convertor

**_A Python script for preparing a SquareSpace blog export for import to Wix._**

---

## How it works

There is no direct support for Squarespace to Wix blog migration. However, Squarespace sites can be exported to a WordPress XML format, and Wix allows you to import blog posts in the form of Wordpress XML feeds. Uploading the Squarespace export directly to Wix will work, but will result in a variety of content and formatting errors (since both sites expect to be working directly with WordPress).

This project acts as a middle-man and aims to fix some of these errors before the blog feed gets to Wix. It uses [BeautifulSoup](https://beautiful-soup-4.readthedocs.io/en/latest/index.html) to process the XML of the RSS feed, as well as the inner HTML of blog contents. I wrote it for a specific use case, and as such the conversion remains _satisfactory_ rather than perfect (see below). Feel free to modify it to suit your organization/personal needs.

## What it does

---

## How to use it

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

## Developer Notes
General Notes
- I avoid using soup.prettify() because it appears to cause issues with Wix's ability to correctly parse the XML

--- 

## License

[^1]: If you set up a [venv using VS Code](https://code.visualstudio.com/docs/python/python-tutorial#_create-a-virtual-environment) like I did, it can conveniently activate every time you open this project