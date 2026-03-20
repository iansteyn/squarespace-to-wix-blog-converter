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

def create_better_content_tag(content_tag):
    if content_tag and content_tag.string:

        inner_soup = BeautifulSoup(content_tag.string, 'html.parser')

        # MOD: # ORDER MATTERS
        remove_summary_block(inner_soup)

        # MOD: # ORDER MATTERS
        fix_paragraph_spacing(inner_soup)

        # MOD: Replace <p class="sqsrte-large"> with <h4> # ORDER MATTERS
        large_text_tags = inner_soup.find_all("p", class_="sqsrte-large")

        for tag in large_text_tags:
            tag.name = 'h4'
            del tag['class']

        # MOD: replace <hr> with <p>---</p>
            # TODO: may require more space - see <br> todo above
        hr_tags = inner_soup.find_all("hr")

        for tag in hr_tags:
            new_tag = soup.new_tag('p')
            new_tag.string = "———"
            tag.replace_with(new_tag)

        # MOD: remove uneccesary divs
        wrapper_div_tags = inner_soup.find_all('div', class_='sqs-html-content')

        for tag in wrapper_div_tags:
            tag.unwrap()

        # TODO: simplify list items
            # For some reason, each list item is its own list, AND is wrapped inside of a <p> on the inside. 
            # I want to simplify this. However, some lists are also structured more normally
        
        # TODO: append links extracted from excerpt
        
        # TODO: remove all remaining extra classes and styles

        # TODO: unescape weird html characters

        # MOD: delete all style and other extraneous tags (can probably happen near the end)
        for tag in inner_soup.find_all(True):
            if tag.has_attr('style'):
                del tag['style']
            if tag.has_attr('data-rte-preserve-empty'):
                del tag['data-rte-preserve-empty']

        # TODO: remove all spans?

        return CData(stringify_soup(inner_soup))
    
## ----
def remove_summary_block(soup: BeautifulSoup):
    """
    Delete Squarespace's large summary block section

    Note: modifies the given `soup` directly
    """
    blocks_to_remove = soup.find_all("div", class_="summary-block-wrapper")
        
    for block in blocks_to_remove:
        block.extract()

def fix_paragraph_spacing(soup: BeautifulSoup):
    """
    Note: modifies the given `soup` directly
    TODO: this doesn't actually work
    older TODO: may have to check whether more <br>s are needed, eg after lists and titles
    """
    p_tags = soup.find_all('p')

    for p in p_tags:
        if p.get_text(strip=True) == '':
            br = soup.new_tag('br')
            p.replace_with(br)
## ----

def create_better_excerpt_tag(excerpt_tag):
    '''
    Doesn't do much yet. 
    '''
    inner_soup = BeautifulSoup(excerpt_tag.string, 'html.parser')

    return CData(stringify_soup(inner_soup))

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