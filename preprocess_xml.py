"""
TODO: file description
TODO: uninstall lxml and dependencies
"""
# -----------------------------------------------
# IMPORTS AND WARNING FILTERS
from bs4 import BeautifulSoup #, XMLParsedAsHTMLWarning
from bs4.element import CData
# import warnings

# warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

# -----------------------------------------------
# FUNCTIONS

def create_better_content_tag(content_tag):
    if content_tag and content_tag.string:

        inner_soup = BeautifulSoup(content_tag.string, 'html.parser')

        # MOD: Delete that summary block section # ORDER MATTERS
        blocks_to_remove = inner_soup.find_all("div", class_="summary-block-wrapper")
        
        for block in blocks_to_remove:
            block.extract()

        # MOD: replace empty <p> tags with <br/> # ORDER MATTERS
            # TODO: may have to check whether more <br>s are needed, eg after lists and titles
        p_tags = inner_soup.find_all('p')

        for p in p_tags:
            if p.get_text(strip=True) == '':
                br = inner_soup.new_tag('br')
                p.replace_with(br)

        # MOD: Replace <p class="sqsrte-large"> with <h4> # ORDER MATTERS
        large_text_tags = inner_soup.find_all("p", class_="sqsrte-large")

        for tag in large_text_tags:
            tag.name = 'h4'
            del tag['class']

        # TODO: replace <hr> with <p>---</p>
        # TODO: remove uneccesary divs
            # learning this will help me with the below task

        # TODO: simplify list items
            # For some reason, each list item is its own list, AND is wrapped inside of a <p> on the inside. 
            # I want to simplify this. However, some lists are also structured more normally
        
        # TODO: append links extracted from excerpt
        
        # TODO: remove all remaining extra classes and styles

        # MOD: delete all style and other extraneous tags (can probably happen near the end)
        for tag in inner_soup.find_all(True):
            if tag.has_attr('style'):
                del tag['style']
            if tag.has_attr('data-rte-preserve-empty'):
                del tag['data-rte-preserve-empty']


        return CData(str(inner_soup.prettify()))

def create_better_excerpt_tag(excerpt_tag):
    '''
    Doesn't do much yet. 
    '''
    inner_soup = BeautifulSoup(excerpt_tag.string, 'html.parser')

    return CData(str(inner_soup))

# ------------------------------------------------------------
# SETUP

# NOTE: the input and output folders may have to be manually created since git doesn't consider directories files
real_input_path = "Squarespace-Wordpress-Export-03-18-2026.xml"
test_input_path = "short-copy-for-testing.xml"
INPUT_FILE_PATH = "./input_xml/" + test_input_path
OUTPUT_FILE_PATH = "./output_xml/" + "modified-rss-feed.xml"

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

print(f"Modified {len(items)} test posts.")

with open(OUTPUT_FILE_PATH, 'w', encoding='utf-8') as file:
    file.write(str(soup.prettify()))
