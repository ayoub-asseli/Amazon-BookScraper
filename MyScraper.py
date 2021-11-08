import requests
from bs4 import BeautifulSoup
import pandas as pd

headers = {"User-Agent": 'your user agent'}

######## SCRAPING FUNCTIONS ########

def get_data_page(url):
    return BeautifulSoup(requests.get(url, headers=headers).content, "html.parser")

def get_next_page_url(soup):
    page = soup.find('ul', {'class': 'a-pagination'})
    if not page.find('li', {'class': 'a-disabled a-last'}):
        url_next_page = 'https://www.amazon.fr' + str(page.find('li', {'class': 'a-last'}).find('a')['href'])
        return url_next_page
    else:
        return

def list_urls_pages(url_page):
    urls = []
    while True:
        soupx = get_data_page(url_page)
        url_page = get_next_page_url(soupx)
        if not url_page:
            break
        urls.append(url_page)
    return urls

def get_items_urls_from_one_page(soup):
    urls = soup.find_all('a', {'class': 'a-link-normal a-text-normal'})
    L_test = []
    for url in urls:
        L_test.append(url['href'])
    fparts = ["https://www.amazon.fr/"]*len(L_test)
    L_urls = []
    for i, j in zip(fparts, L_test):
        L_urls.append(i+j)
    return L_urls

def get_items_urls_from_all_pages(url):
    list_urls = list_urls_pages(url)
    items_urls = []
    for url1 in list_urls:
        soup = get_data_page(url1)
        items_urls += get_items_urls_from_one_page(soup)
    return items_urls

######## SCRAPING ITEM ########

def get_item_title(soup):
    title = soup.find('span', {'id': 'productTitle'})
    return title.text.replace('\n', '')

def get_item_prices_formats(soup):
    ul = soup.find('ul', {'class': 'a-unordered-list a-nostyle a-button-list a-horizontal'})
    span1 = ul.find_all('span', {'class': 'a-list-item'})
    span2 = ul.find_all('span', {'class': 'a-list-item'})
    spans = span1 + span2
    res1 = []
    for span in spans:
        format_price = span.text
        if 'Broché' in format_price:
            res1.append(format_price)
        elif 'Kindle' in format_price:
            res1.append(format_price)
        elif 'Relié' in format_price:
            res1.append(format_price)
        elif 'Poche' in format_price:
            res1.append(format_price)
    return cleaner_prices(res1)

def get_item_evaluation(soup):
    note = soup.find('span', {'id': 'acrPopover'})['title'].split('sur')[0].strip()
    link = soup.find('a', {'id': 'acrCustomerReviewLink'})
    number_of_evaluations = link.find('span', {'id': 'acrCustomerReviewText'}).text.split()
    number_of_evaluations = ''.join(number_of_evaluations[:len(number_of_evaluations)-1])
    return note, number_of_evaluations

def get_links_for_each_item_format(soup):
    div = soup.find('div', {'id': 'tmmSwatches'})
    ul = div.find('ul', {'class': 'a-unordered-list a-nostyle a-button-list a-horizontal'})
    format_selected = ul.find_all('span', {'class': 'a-button-inner'})
    formats_unselected = ul.find_all('span', {'class': 'a-button-inner'})
    formats = formats_unselected + format_selected
    res = []
    for format in formats:
        link = format.find('a', {'class': 'a-button-text'})['href']
        fort = format.find(lambda tag: tag.name == 'span' and not tag.attrs).text
        res.append(("https://www.amazon.fr/"+link, fort))
    return(res)

def get_item_number_of_page(url):
    soup = get_data_page(url)
    div = soup.find('div', {'id': 'detailBullets_feature_div'})
    ul = div.find('ul', {'class': 'a-unordered-list a-nostyle a-vertical a-spacing-none detail-bullet-list'})
    li = ul.find_all(lambda tag: tag.name == 'li' and not tag.attrs)
    number_of_pages1 = li[2].find('span', {'class': 'a-list-item'}).text.split()
    number_of_pages2 = li[3].find('span', {'class': 'a-list-item'}).text.split()
    test = li[0].find('span', {'class': 'a-list-item'}).text.split()
    if 'ASIN' in test:
        return number_of_pages2[2]
    else:
        return number_of_pages1[2]

def get_file_size_kindle(url):
    soup = get_data_page(url)
    div = soup.find('div', {'id': 'detailBullets_feature_div'})
    ul = div.find('ul', {'class': 'a-unordered-list a-nostyle a-vertical a-spacing-none detail-bullet-list'})
    li = ul.find_all(lambda tag: tag.name == 'li' and not tag.attrs)
    size_file1 = li[2].find('span', {'class': 'a-list-item'}).text.split()
    size_file2 = li[3].find('span', {'class': 'a-list-item'}).text.split()
    test = li[0].find('span', {'class': 'a-list-item'}).text.split()
    if 'ASIN' in test:
        return " ".join(size_file2[4:])
    else:
        return " ".join(size_file1[4:])

def get_item_dimension(url):
    soup = get_data_page(url)
    div = soup.find('div', {'id': 'detailBullets_feature_div'})
    ul = div.find('ul', {'class': 'a-unordered-list a-nostyle a-vertical a-spacing-none detail-bullet-list'})
    li = ul.find_all(lambda tag: tag.name == 'li' and not tag.attrs)
    dim = li[len(li) - 1].find('span', {'class': 'a-list-item'}).text.split()
    return " ".join(dim[2:])

def get_item_broché_dimension(url, res):
    for elem in res:
        if 'Broché' in elem[1] and 'javascript' in elem[0]:
            dimension = get_item_dimension(url)
        elif 'Broché' in elem[1]:
            url = elem[0]
            dimension = get_item_dimension(url)
    return dimension

def get_item_poche_dimension(url, res):
    for elem in res:
        if 'Poche' in elem[1] and 'javascript' in elem[0]:
            dimension = get_item_dimension(url)
        elif 'Poche' in elem[1]:
            url = elem[0]
            dimension = get_item_dimension(url)
    return dimension

def get_item_relié_dimension(url, res):
    for elem in res:
        if 'Relié' in elem[1] and 'javascript' in elem[0]:
            dimension = get_item_dimension(url)
        elif 'Relié' in elem[1]:
            url = elem[0]
            dimension = get_item_dimension(url)
    return dimension

def get_item_broché_number_of_pages(url, res):
    for elem in res:
        if 'Broché' in elem[1] and 'javascript' in elem[0]:
            nb_pages = get_item_number_of_page(url)
        elif 'Broché' in elem[1]:
            url = elem[0]
            nb_pages = get_item_number_of_page(url)
    return nb_pages

def get_item_poche_number_of_pages(url, res):
    for elem in res:
        if 'Poche' in elem[1] and 'javascript' in elem[0]:
            nb_pages = get_item_number_of_page(url)
        elif 'Poche' in elem[1]:
            url = elem[0]
            nb_pages = get_item_number_of_page(url)
    return nb_pages

def get_item_relié_number_of_pages(url, res):
    for elem in res:
        if 'Relié' in elem[1] and 'javascript' in elem[0]:
            nb_pages = get_item_number_of_page(url)
        elif 'Relié' in elem[1]:
            url = elem[0]
            nb_pages = get_item_number_of_page(url)
    return nb_pages

def get_item_file_size_kindle(url, res):
    for elem in res:
        if 'Kindle' in elem[1] and 'javascript' in elem[0]:
            file_size = get_file_size_kindle(url)
        elif 'Kindle' in elem[1]:
            url = elem[0]
            file_size = get_file_size_kindle(url)
    return file_size

######## CLEANER FUNCTIONS ########

def cleaner_prices(text):
    text2 = []
    for c in text:
        text2.append(c.replace('\n', '').replace('EmpruntCe titre et plus d’un million d’autres sont disponibles sur Abonnement Kindle. Le prix d\'emprunt à la page est disponible ici.','').replace('à partir de', ''))
    text3 = []
    for c in text2:
        text3.append(c.split('\xa0€')[0])
    return list(set(text3))

######## CREATION OF MY DATAFRAME ########

# Get all my data in order to generate my csv file
def generate_my_items_table(items_urls):
    table = []
    item = []
    for item_url in items_urls:
        soup = get_data_page(item_url)
        try:
            item.append(get_item_title(soup))
        except:
            item = []
            continue
        try:
            item.append(cleaner_prices(get_item_prices_formats(soup)))
        except:
            item = []
            continue
        try:
            links = get_links_for_each_item_format(soup)
            nb_pages = get_item_broché_number_of_pages(item_url, links)
            item.append(nb_pages)
        except:
            item.append('None')
        try:
            links = get_links_for_each_item_format(soup)
            file_size = get_item_file_size_kindle(item_url, links)
            item.append(file_size)
        except:
            item.append('None')
        try:
            links = get_links_for_each_item_format(soup)
            nb_pages = get_item_poche_number_of_pages(item_url, links)
            item.append(nb_pages)
        except:
            item.append('None')
        try:
            links = get_links_for_each_item_format(soup)
            nb_pages = get_item_relié_number_of_pages(item_url, links)
            item.append(nb_pages)
        except:
            item.append('None')
        try:
            links = get_links_for_each_item_format(soup)
            dimension = get_item_broché_dimension(item_url, links)
            item.append(dimension)
        except:
            item.append('None')
        try:
            links = get_links_for_each_item_format(soup)
            dimension = get_item_poche_dimension(item_url, links)
            item.append(dimension)
        except:
            item.append('None')
        try:
            links = get_links_for_each_item_format(soup)
            dimension = get_item_relié_dimension(item_url, links)
            item.append(dimension)
        except:
            item.append('None')
        try:
            item.append(get_item_evaluation(soup)[0])
            item.append(get_item_evaluation(soup)[1])
        except:
            item.append('None')
            item.append('None')
        item.append(item_url)
        mar = tuple(item)
        print(mar)
        table.append(mar)
        item = []
    return table


# Get the first search page

recherche = 'livre recette minceur'
url = "https://www.amazon.fr/s?k={}&i=stripbooks&__mk_fr_FR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&ref=nb_sb_noss_1".format('+'.join(recherche.split()))
soup = get_data_page(url)
items_url = get_items_urls_from_all_pages(url)
table = generate_my_items_table(items_url[:10])

books = pd.DataFrame(table, columns=['Titres', '[Formats, Prix]', 'Nombre de pages Format Broché', 'Taille du fichier Kindle' ,'Nombre de pages Format Poche', 'Nombre de pages Format Relié', 'Dimensions Format Broché', 'Dimensions Format Poche', 'Dimensions Format Relié', 'Evaluations (sur 5)', 'Nombre d\'évaluations', 'Liens' ])
books.to_csv('test_fx.csv')
