"""
TODO: file description

General Notes
- I avoid using soup.prettify() because it appears to cause issues with Wix's ability to correctly parse the XML
"""
# -----------------------------------------------
# IMPORTS AND WARNING FILTERS
from bs4 import BeautifulSoup #, XMLParsedAsHTMLWarning
from bs4.element import CData
# import warnings

# warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

# ---------------------------------------------------
# CONSTANTS/CONFIG
# these are things which should be made into parameters if I publish this script for general use

# NOTE: the input and output folders may have to be manually created since git doesn't consider directories files
real_input_path = "Squarespace-Wordpress-Export-03-18-2026.xml"
test_input_path = "short-copy-for-testing.xml"
INPUT_FILE_PATH = "./input_xml/" + test_input_path
OUTPUT_FILE_PATH = "./output_xml/" + "modified-rss-feed.xml"

PRETTIFY = True # NOTE: Set to false for final output that gets uploaded to Wix

# -----------------------------------------------
# FUNCTIONS

# TODO: clean content
def create_better_content_tag(content_tag) -> CData:
    if content_tag and content_tag.string:

        inner_soup = BeautifulSoup(content_tag.string, 'html.parser')

        # Remember: ORDER MATTERS

        # REMOVE JUNK
        remove_summary_block(inner_soup)
        remove_extra_wrappers(inner_soup) # TODO actually this and r_e_p and a_p_s must be a linear process so they should be combined into one function here perhaps
        remove_empty_paragraphs(inner_soup)

        # FIXES
        replace_divider_lines(inner_soup)
        fix_headings(inner_soup)
        # TODO XXX!!!: append links extracted from excerpt
        add_paragraph_spacers(inner_soup)

        # FINAL CLEAN-UP
        remove_extra_attributes(inner_soup, [
            'style',
            'class',
            'data-rte-preserve-empty',
            'data-rte-list'
        ])

        return CData(stringify_soup(inner_soup))
    
## ----
def remove_summary_block(soup: BeautifulSoup) -> None:
    """
    Delete Squarespace's large summary block section

    Note: modifies the given `soup` directly
    """
    blocks_to_remove = soup.find_all("div", class_="summary-block-wrapper")
        
    for block in blocks_to_remove:
        block.extract()

def remove_extra_wrappers(soup: BeautifulSoup) -> None:
    """
    Unwraps all uneccessary divs and spans
    """
    wrapper_div_tags = soup.find_all('div', class_='sqs-html-content')

    for tag in wrapper_div_tags:
        tag.unwrap()

    wrapper_span_tags = soup.find_all('span')

    for tag in wrapper_span_tags:
        tag.unwrap()

def remove_empty_paragraphs(soup:BeautifulSoup) -> None:
    """
    delete all empty p tags
    """
    p_tags = soup.find_all('p')

    for p in p_tags:
        if p.get_text(strip=True) == '':
            p.extract()

def add_paragraph_spacers(soup: BeautifulSoup) -> None:
    """
    Ensures that there is spacing between paragraphs, titles, etc.

    Kind of a hacky fix because it uses `<h6>` headings as spacers, but its all I could get Wix to respect.
    """
    top_level_tags = soup.find_all(True, recursive=False)

    for tag in top_level_tags:
        tag.insert_after(soup.new_tag('h6'))

def replace_divider_lines(soup: BeautifulSoup) -> None:
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

def remove_extra_attributes(soup: BeautifulSoup, attributes: list[str]) -> None:
    for tag in soup.find_all(True):
        for attr in attributes:
            if tag.has_attr(attr):
                del tag[attr]
## ----

def create_better_excerpt_tag(excerpt_tag):
    '''
    TODO
    Doesn't do much yet. 
    '''
    inner_soup = BeautifulSoup(excerpt_tag.string, 'html.parser')

    return CData(stringify_soup(inner_soup))

# TODO: unescape weird html characters in titles?

# HELPERS
def stringify_soup(soup: BeautifulSoup):
    """
    Returns a string representation of the given `soup`, formatted according to the global script settings.
    """
    if PRETTIFY:
        return soup.prettify()
    else:
        return str(soup)

# ------------------------------------------------------------
# SETUP


with open(INPUT_FILE_PATH, 'rb') as file:
    soup = BeautifulSoup(file, 'xml') # using html.parser instead of xml, because lxml strips CDATA and messes everything up

# -----------------------------------
# LOOP THROUGH ITEMS
items = soup.find_all('item')

for item in items:

    content_tag = item.find('content:encoded')
    content_tag.string = create_better_content_tag(content_tag)
    
    excerpt_tag = item.find('excerpt:encoded')
    excerpt_tag.string = create_better_excerpt_tag(excerpt_tag)

# --------------------------------
# FINISH

with open(OUTPUT_FILE_PATH, 'w', encoding='utf-8') as file:
    file.write(stringify_soup(soup))

print(f"Modified {len(items)} test posts.")