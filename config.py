# CONFIG GLOBALS
"""
Script configuration constants. Edit these as you wish.

- `INPUT_FILE_PATH: str`
    - Location of the input file, i.e. the XML file you exported from SquareSpace.
- `OUTPUT_FILE_PATH: str`
    - Location to write the output file to. Should end in `.xml`. This is the file you will upload to Wix.
- `MESSAGE_FOR_EXTRACTED_LINKS: str`
    - A message explaining the extracted links attached at the bottom of each post.
    - Tailor to your audience.
- `CATEGORY_NAME_MAP: dict[str, str]`
    - Dictionary with categories you want to rename, with entries in the form "old_name":"new_name". Can be empty.
- `PRETTIFY: bool`
    - Only set to `True` when testing (makes the xml output easier to read).
    - This MUST be set to `False` when generating the final document for Wix. 

"""

real_input_path = "Squarespace-Wordpress-Export-04-02-2026.xml"
test_input_path = "short-copy-for-testing.xml"

INPUT_FILE_PATH = "./input_xml/" + real_input_path
"""
Location of the input file, i.e. the XML file you exported from SquareSpace.
"""

OUTPUT_FILE_PATH = "./output_xml/" + "modified-rss-feed.xml"
"""
Location to write the output file to. Should end in `.xml`. This is the file you will upload to Wix.
"""

MESSAGE_FOR_EXTRACTED_LINKS = (
    "This article was migrated from our old archive. The following links were preserved from the original publication:"
)
"""
- A message explaining the extracted links attached at the bottom of each post.
- Tailor to your audience.
"""

CATEGORY_NAME_MAP = {
    'Planetary Health': 'Climate Action',
    'Event': 'Events'
}
"""
Dictionary with categories you want to rename, with entries in the form `"old_name":"new_name"`. Can be empty.
"""

NON_POST_URLS = ['/events']
"""
TODO: description
"""

PRETTIFY = False
"""
- Only set to `True` when testing (makes the xml output easier to read).
- This MUST be set to `False` when generating the final document for Wix. 
"""