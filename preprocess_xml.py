from bs4 import BeautifulSoup

# NOTE: the input and output folders may have to be manually created since git doesn't consider directories files
INPUT_FILE_PATH = "./input_xml/" + "Squarespace-Wordpress-Export-03-18-2026.xml"
OUTPUT_FILE_PATH = "./output_xml/" + "modified-rss-feed.xml"


# According to Gemini: Using 'rb' (read binary) is safer for large XML files
# as it lets the parser handle the encoding declaration automatically'rb' 
with open(INPUT_FILE_PATH, 'rb') as file:
    soup = BeautifulSoup(file, 'xml')

blog_title = soup.find('title')

blog_title.string = "New Title"


# FINISH
with open(OUTPUT_FILE_PATH, 'w', encoding='utf-8') as file:
    file.write(str(soup))

