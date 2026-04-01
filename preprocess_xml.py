"""
TODO: file description

General Notes
- I avoid using soup.prettify() because it appears to cause issues with Wix's ability to correctly parse the XML
"""
# ---------------------------------------------------
# IMPORTS
from bs4 import BeautifulSoup, Tag, CData
import copy

# ---------------------------------------------------
# CONFIG GLOBALS
"""
Script configuration constants. Edit these as you wish.

- `INPUT_FILE_PATH: str`
    - Location of the input file, i.e. the XML file you exported from SquareSpace.
- `OUTPUT_FILE_PATH: str`
    - Location to write the output file to. Should end in `.xml`. This is the file you will upload to Wix.
- `PRETTIFY: bool`
    - Only set to `True` when testing (makes the xml output easier to read).
    - This MUST be set to `False` when generating the final document for Wix. 
"""

real_input_path = "Squarespace-Wordpress-Export-03-18-2026.xml"
test_input_path = "short-copy-for-testing.xml"

INPUT_FILE_PATH = "./input_xml/" + test_input_path
OUTPUT_FILE_PATH = "./output_xml/" + "modified-rss-feed.xml"
PRETTIFY = True

# ---------------------------------------------------
# SCRIPT

def main() -> None:
    """
    The actual script logic. Called at the bottom of this file.
    """

    # SETUP
    with open(INPUT_FILE_PATH, 'rb') as file:
        xml_soup = BeautifulSoup(file, 'xml')

    # LOOP THROUGH ITEMS
    items = xml_soup.find_all('item')

    for item in items:

        excerpt_tag = item.find('excerpt:encoded')
        content_tag = item.find('content:encoded')
        title_tag = item.find('title')

        # This is unlikely, but just in case:
        # if not excerpt_tag and not content_tag:
        #     continue

        extracted_links = extract_excerpt_links(excerpt_tag.string)

        excerpt_tag.string = get_clean_excerpt(excerpt_tag.string)
        content_tag.string = get_clean_content(content_tag.string, extracted_links)

        title_tag.string = get_clean_title(title_tag.string)

    # FINISH
    with open(OUTPUT_FILE_PATH, 'w', encoding='utf-8') as file:
        file.write(stringify_soup(xml_soup))

    print(f"Modified {len(items)} posts.")

# -----------------------------------------------
# FUNCTIONS

def get_clean_content(content:str, excerpt_links: list[Tag] = []) -> CData:
    """
    Removes squarespace junk, fixes formatting, cleans up HTMl, and (optionally) appends `excerpt_links`. 
    
    Returns a version of the given `content` string as a cleaned `CData` object,
    ready to be reassigned to the `.string` property of the content tag.
    """

    content_soup = BeautifulSoup(content, 'html.parser')

    # Remember: ORDER MATTERS

    # (1) REMOVE SQUARESPACE JUNK
    remove_summary_block(content_soup)
    remove_extra_wrappers(content_soup)
    remove_empty_paragraphs(content_soup)

    # (2) FIX FORMATTING
    fix_divider_lines(content_soup)
    fix_headings(content_soup) # must happen after remove_empty_paragraphs
    fix_spacing(content_soup) # must happen after remove_extra_wrappers

    # (3) HTML CLEAN-UP
    remove_extra_attributes(content_soup) # must happen after fix_headings

    # (4) APPEND EXCERPT LINKS
    # (this is to somewhat compensate for the loss of SquareSpace's link buttons)
    append_links(content_soup, excerpt_links) # must happen after all

    return CData(stringify_soup(content_soup))

## ----
def remove_summary_block(soup: BeautifulSoup) -> None:
    """
    Delete Squarespace's large summary block section

    Note: modifies the given `soup` directly
    """
    blocks_to_remove = soup.find_all("div", class_="summary-block-wrapper")

    for block in blocks_to_remove:
        block.decompose()

def remove_extra_wrappers(soup: BeautifulSoup) -> None:
    """
    Unwraps all uneccessary divs and spans
    """
    extra_divs = soup.find_all('div')
    extra_spans = soup.find_all('span')

    for tag in (extra_divs + extra_spans):
        tag.unwrap()

def remove_empty_paragraphs(soup:BeautifulSoup) -> None:
    """
    delete all empty p tags
    """
    p_tags = soup.find_all('p')

    for p in p_tags:
        if p.get_text(strip=True) == '':
            p.decompose()

def remove_extra_attributes(
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

def fix_spacing(soup: BeautifulSoup) -> None:
    """
    Ensures that there is spacing between paragraphs, titles, and other top-level elements.

    Kind of a hacky fix because it uses `<h6>` headings as spacers, but its all I could get Wix to respect.
    """
    top_level_tags = soup.find_all(True, recursive=False)

    for tag in top_level_tags:
        tag.insert_after(soup.new_tag('h6'))

def fix_divider_lines(soup: BeautifulSoup) -> None:
    """
    Wix doesn't use `<hr>` elements. Replace them with `<p>---</p>` in case the visual division was important.
    """
    # TODO: may require more space - see <br> todo above
    hr_tags = soup.find_all("hr")

    for tag in hr_tags:
        new_tag = soup.new_tag('p')
        new_tag.string = "———"
        tag.replace_with(new_tag)

def fix_headings(soup: BeautifulSoup) -> None:
    """
    Replaces `<p class="sqsrte-large">` with `<h4>` so they register as actual headings
    """
    large_text_tags = soup.find_all("p", class_="sqsrte-large")

    for tag in large_text_tags:
        tag.name = 'h4'

def append_links(soup: BeautifulSoup, link_list: list[Tag]) -> None:
    """
    Appends links to `soup` in a nicely formatted manner.
    """

    if not link_list:
        return

    divider = soup.new_tag('p')
    divider.string = '———'

    spacer1 = soup.new_tag('h6')
    spacer2 = soup.new_tag('h6')

    heading = soup.new_tag('h4')
    heading.string = 'Links'

    ul = soup.new_tag('ul')

    for a_tag in link_list:
        li = soup.new_tag('li')
        li.append(a_tag)
        ul.append(li)

    for tag in [divider, spacer1, heading, spacer2, ul]:
        soup.append(tag)

## ----

def get_clean_excerpt(excerpt:str) -> CData:
    '''
    Basically just unwraps all tags and returns a plaintext (but still CData-encased) version of the excerpt
    '''
    excerpt_soup = BeautifulSoup(excerpt, 'html.parser')

    all_tags = excerpt_soup.find_all(True)

    for tag in all_tags:
        tag.unwrap()

    return CData(stringify_soup(excerpt_soup))

def extract_excerpt_links(excerpt:str) -> list[Tag]:
    '''
    Returns a list of `<a>` tags (as `Tag` objects) extracted from the given `excerpt`
    '''
    excerpt_soup = BeautifulSoup(excerpt, 'html.parser')

    extracted_tags = []
    a_tags = excerpt_soup.find_all('a')

    for a in a_tags:
        extracted_tags.append(copy.copy(a))

    return extracted_tags

## ----

# TODO: unescape weird html characters in titles?
"""
Problem definition:
all strings outside of CDATA blocks (i.e., titles, links, post names) that contained HTML escape
characters seem to have been doubly escaped. For example, `&nbsp;` becomes `&amp;nbsp;`

Actually it's more complicated - some links seem to just have nbsp tacked on to the back?
"""

# def fix_escape_chars(item:Tag):
#     # get the tags:
#     # title - for &amp;amp; and &amp;nbsp
#     # link - for plain nbsp
#     # wp:post_name - for plain nbsp

#     title_tag = item.find('title')
#     link_tag = item.find('link')
#     post_name_tag = item.find('wp:post_name')

#     title_tag.string = _strip_nbsp(title_tag.string)


#     pass

def get_clean_title(title:str) -> str:
    """
    Returns a cleaned copy of `title`
    Fixes double-escaped ampersands and removes unnecessary non-breaking spaces.
    """
    return title.replace("&nbsp;", "").replace("&amp;", "&")


# ---- 

# possible TODO: normalize category names

# ----

def stringify_soup(soup: BeautifulSoup) -> str:
    """
    Returns a string representation of the given `soup`, formatted according to the global script settings.
    """
    if PRETTIFY:
        return soup.prettify()
    else:
        return str(soup)

# ------------------------------------------------------------
# SCRIPT EXECUTION

if __name__ == "__main__":
    main()