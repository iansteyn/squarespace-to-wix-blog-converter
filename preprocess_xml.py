"""
convert.py
----------
Converts an exported Squarespace blog feed to a format that is ready to be imported into Wix. See README.md for usage details.

General Notes (TODO: remove)
- I avoid using soup.prettify() because it appears to cause issues with Wix's ability to correctly parse the XML

----------

Edit the global constants below to configure the script settings. 

INPUT_FILE_PATH:
    (str) Location of the input file, i.e. the XML file you exported from SquareSpace.

OUTPUT_FILE_PATH:
    (str) Location to write the output file to. Should end in `.xml`. This is the file you will upload to Wix.

MESSAGE_FOR_EXTRACTED_LINKS:
    (str) A message explaining the extracted links attached at the bottom of each post. Tailor to your audience.

CATEGORY_NAME_MAP:
    (dict) Dictionary with categories you want to rename, with entries in the form "old_name":"new_name". Can be empty.

NON_POST_URLS: list
    (list) List of urls that will indicate an item is not a blog post. Items with these links will be deleted.
    (Squarespace exports a website's pages to the same rss feed as blog posts.)

PRETTIFY:
    (bool) Only set to `True` when testing (makes the xml output easier to read).
    This MUST be set to `False` when generating the final document for Wix. 
"""
# ---------------------------------------------------
# CONFIG GLOBALS

INPUT_FILE_PATH = (
    "./input_xml/Squarespace-Wordpress-Export-04-02-2026.xml"
)
OUTPUT_FILE_PATH = (
    "./output_xml/modified-rss-feed.xml"
)
MESSAGE_FOR_EXTRACTED_LINKS = (
    "This article was migrated from our old archive. The following links were preserved from the original publication:"
)
CATEGORY_NAME_MAP = {
    'Planetary Health': 'Climate Action',
    'Event': 'Events'
}
NON_POST_URLS = [
    '/events'
]
PRETTIFY = False

# ---------------------------------------------------
# IMPORTS
from bs4 import BeautifulSoup, CData

# ---------------------------------------------------
# SCRIPT

def main() -> None:
    """
    The actual script logic. Called at the bottom of this file.
    """

    # SETUP
    with open(INPUT_FILE_PATH, 'rb') as file:
        xml_soup = BeautifulSoup(file, 'xml')

    # LOOP THROUGH RSS FEED ITEMS
    items = xml_soup.find_all('item')
    num_posts = len(items)

    for item in items:

        # (1) Find Tags
        content = item.find('content:encoded')
        excerpt = item.find('excerpt:encoded')
        title = item.find('title')
        link = item.find('link')
        post_name = item.find('wp:post_name')
        categories = item.find_all('category')
        attachment_url = item.find('wp:attachment_url')

        # (2) Delete item if not relevant
        if (
            attachment_url                   # It is just an attachment (these don't get transferred to Wix)
            or not title.string              # no title (it's a junk item)
            or "(Copy)" in title.string      # post is a copy
            or link.string in NON_POST_URLS  # item is not a post
        ):
            item.decompose()
            num_posts -= 1
            continue

        # (3) extract links from excerpt BEFORE cleaning
        extracted_links = extract_links(excerpt.string)

        # (4) CLEAN tags
        single_tags_to_clean = [
            (content, get_clean_content),
            (excerpt, get_clean_excerpt),
            (title, get_clean_title),
            (link, get_clean_link),
            (post_name, get_clean_post_name)
        ]

        for tag, cleaner in single_tags_to_clean:
            if tag and tag.string:
                tag.string = cleaner(tag.string)

        for category_tag in categories:
            if category_tag and category_tag.string:
                category_tag.string = get_clean_category(category_tag.string, CATEGORY_NAME_MAP)

        # (5) extract links from content AFTER cleaning
        extracted_links += extract_links(content.string)

        # (6) append all extracted links to content
        if extracted_links:
            content.string = append_links(content.string, extracted_links)

    # FINISH
    with open(OUTPUT_FILE_PATH, 'w', encoding='utf-8') as file:
        file.write(_stringify_soup(xml_soup))

    print(f"Modified {num_posts} posts.")


# -----------------------------------------------
# FUNCTIONS

# ----
# CLEANER FUNCTIONS

def get_clean_content(content:str) -> CData:
    """
    Removes squarespace junk, fixes formatting, cleans up HTML. 
    
    Returns a version of the given `content` string as a cleaned `CData` object,
    ready to be reassigned to the `.string` property of the content tag.
    """

    content_soup = BeautifulSoup(content, 'html.parser')

    # Remember: ORDER MATTERS

    # (1) REMOVE SQUARESPACE JUNK
    _remove_summary_block(content_soup)
    _remove_extra_wrappers(content_soup)
    _remove_empty_paragraphs(content_soup)

    # (2) FIX FORMATTING
    _fix_divider_lines(content_soup)
    _fix_headings(content_soup) # must happen after remove_empty_paragraphs
    _fix_spacing(content_soup) # must happen after remove_extra_wrappers

    # (3) HTML CLEAN-UP
    _remove_extra_attributes(content_soup) # must happen after fix_headings

    return CData(_stringify_soup(content_soup))

def get_clean_excerpt(excerpt:str) -> CData:
    '''
    Basically just unwraps all tags and returns a plaintext (but still CData-encased) version of the excerpt
    '''
    excerpt_soup = BeautifulSoup(excerpt, 'html.parser')

    all_tags = excerpt_soup.find_all(True)

    for tag in all_tags:
        tag.unwrap()

    return CData(_stringify_soup(excerpt_soup))

def get_clean_title(title:str) -> CData:
    """
    Returns a cleaned copy of `title`.

    (Fixes double-escaped ampersands and removes unnecessary non-breaking spaces).
    """
    return CData(title.replace("&nbsp;", "").replace("&amp;", "&"))

def get_clean_link(link:str) -> str:
    """
    Returns a cleaned copy of `link`.
    
    (Removes "nbsp" suffixes).
    """
    return link.replace("nbsp", "")

def get_clean_post_name(post_name:str) -> str:
    """
    Returns a cleaned copy of `post_name`.

    (Removes "nbsp" suffixes).
    """
    return post_name.replace("nbsp", "")

def get_clean_category(category:str, category_name_map:dict[str, str]) -> CData:
    """
    Returns a cleaned copy of `category`.

    Normalizes white space and capitalization, and maps some categories to new names.
    """
    # (1) normalize white space and capitalization
    clean_category = category.title().strip()

    # (2) map any categories that need to be merged into one
    for old_name, new_name in category_name_map.items():
        if clean_category == old_name:
            clean_category = new_name

    return CData(clean_category)

# ----
# HELPERS FOR CLEANERS

def _remove_summary_block(soup: BeautifulSoup) -> None:
    """
    Delete Squarespace's large summary block section

    Note: modifies the given `soup` directly
    """
    blocks_to_remove = soup.find_all("div", class_="summary-block-wrapper")

    for block in blocks_to_remove:
        block.decompose()

def _remove_extra_wrappers(soup: BeautifulSoup) -> None:
    """
    Unwraps all uneccessary divs and spans
    """
    extra_divs = soup.find_all('div')
    extra_spans = soup.find_all('span')

    for tag in (extra_divs + extra_spans):
        tag.unwrap()

def _remove_empty_paragraphs(soup:BeautifulSoup) -> None:
    """
    delete all empty p tags
    """
    p_tags = soup.find_all('p')

    for p in p_tags:
        if p.get_text(strip=True) == '':
            p.decompose()

def _remove_extra_attributes(
        soup: BeautifulSoup,
        attributes: list[str] = ['style', 'class', 'data-rte-preserve-empty', 'data-rte-list']
) -> None:
    """
    Strips all tags in `soup` of extra, unnecessary attributes.
    
    By default, these are `style`, `class`, `data-rte-preserve-empty`, and `data-rte-list`. A different list of `attributes` can be passed optionally.
    """
    for tag in soup.find_all(True):
        for attr in attributes:
            if tag.has_attr(attr):
                del tag[attr]

def _fix_spacing(soup: BeautifulSoup) -> None:
    """
    Ensures that there is spacing between paragraphs, titles, and other top-level elements.

    Kind of a hacky fix because it uses `<h6>` headings as spacers, but its all I could get Wix to respect.
    """
    top_level_tags = soup.find_all(True, recursive=False)

    for tag in top_level_tags:
        tag.insert_after(soup.new_tag('h6'))

def _fix_divider_lines(soup: BeautifulSoup) -> None:
    """
    Wix doesn't use `<hr>` elements. Replace them with `<p>---</p>` in case the visual division was important.
    """
    hr_tags = soup.find_all("hr")

    for tag in hr_tags:
        new_tag = soup.new_tag('p')
        new_tag.string = "———"
        tag.replace_with(new_tag)

def _fix_headings(soup: BeautifulSoup) -> None:
    """
    Replaces `<p class="sqsrte-large">` with `<h4>` so they register as actual headings
    """
    large_text_tags = soup.find_all("p", class_="sqsrte-large")

    for tag in large_text_tags:
        tag.name = 'h4'

# ----
# LINK EXTRACTION/INSERTION FUNCTIONS

def extract_links(html:str, ignore_img_links:bool = True) -> list[dict[str, str]]:
    '''
    Extracts all links from the given `html` string.
    
    By default, ignores image links (`<a><img></a>`) (since these are actually transferred to Wix), but
    you can change this can by setting the parameter `ignore_img_links=False`.
    
    Returns a list in the format:
    ```python
    [
        {
            'text': 'linktext',
            'url': 'https://somelink.com'
        },
        {
            'text': 'sometext',
            'url': 'mailto:example@example.com'
        }
    ]
    ```
    '''
    soup = BeautifulSoup(html, 'html.parser')

    extracted_links = []
    a_tags = soup.select('a[href]')

    for a in a_tags:
        if ignore_img_links and a.find('img'):
            continue

        extracted_links.append({
            'text': a.string,
            'url': a['href']
        })

    return extracted_links

def append_links(content: str, links: list[dict[str, str]]) -> CData:
    """
    Appends the given `links` to a copy of `content` in a plaintext, markdown-like format.

    Wix sanitizes most links on import (e.g. `<a>linktext</a>` --> `linktext`).
    This function is a workaround for including link data that cannot otherwise be included.
    
    Returns a copy of the given `content` string with `excerpt_links` appended, as a `CData` object
    ready to be reassigned to the `.string` property of the content tag. The format of the appended links is:
    ```
    <p>———</p>
    <h6></h6>
    <h4>Links</h4>
    <p>Message about the links</p>
    <h6></h6>
    <ul>
      <li>[linktext](linkurl)</li>
      ...
    </ul>
    ```
    """
    content_soup = BeautifulSoup(content, 'html.parser')

    # create stuff before links
    divider = content_soup.new_tag('p')
    divider.string = '———'

    spacer1 = content_soup.new_tag('h6')
    spacer2 = content_soup.new_tag('h6')

    heading = content_soup.new_tag('h4')
    heading.string = 'Links'

    message = content_soup.new_tag('p')
    message.string = MESSAGE_FOR_EXTRACTED_LINKS

    ul = content_soup.new_tag('ul')

    for tag in [divider, spacer1, heading, message, spacer2, ul]:
        content_soup.append(tag)

    # insert links
    for link in links:
        li = content_soup.new_tag('li')
        li.string = _format_link(link) 
        ul.append(li)

    return CData(_stringify_soup(content_soup))

# ----
# HELPERS FOR LINK FUNCTIONS
def _format_link(link: dict[str, str]) -> str:
    """
    Formats a given `link` dictionary with keys `text` and `url` as markdown-like plaintext.

    Square brackets are encoded as escaped html entities because Wix ignores and deletes `[` `]` unless they are escaped.
    """
    text = link['text'] or 'Unnamed Link'
    url = link['url'] or 'Missing URL'

    return f"&#91;{text}&#93;({url})" # i.e. `[text](url)`

# ----
# GENERAL HELPERS

def _stringify_soup(soup: BeautifulSoup) -> str:
    """
    Returns a string representation of the given `soup`, formatted according to the global script settings.
    """
    # formatter=None is used to avoid unnecessarily double escaping html entity characters
    if PRETTIFY:
        return soup.prettify(formatter=None)
    else:
        return soup.decode(formatter=None)

# ------------------------------------------------------------
# SCRIPT EXECUTION

if __name__ == "__main__":
    main()