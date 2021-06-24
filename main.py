import csv
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import os





def extraction(page_url):
    book_review_scraper = {}
    # bring back url
    req = requests.get(page_url)
    if req.ok:
        # création of soupe object
        soup = BeautifulSoup(req.text, 'lxml')

        # création of the variable prod_inf
        # looking for informations first in table then find class table table-striped and finally find all td markers
        prod_inf = soup.find('table', {'class': 'table table-striped'}).find_all('td')

        # extration of book informatons and filled my empty dictionnaty
        book_review_scraper['product_page_url'] = req.url
        book_review_scraper['universal_product_code'] = prod_inf[0].text
        book_review_scraper['title'] = soup.find('ul', {'class': 'breadcrumb'}).find_all('li')[3].text
        book_review_scraper['price_including_tax'] = prod_inf[3].text.replace("Â", "")
        book_review_scraper['price_excluding_tax'] = prod_inf[2].text.replace("Â", "")
        book_review_scraper['availability'] = prod_inf[5].text

        #condition if the "product description" is none signal : no description else continu to scrap
        if soup.find('div', {'id': 'product_description'}) is None:
            book_review_scraper['product_description'] = 'No desccription is available'
        else:
            book_review_scraper['product_description'] = soup.find('div', {'id': 'product_description'}).findNext('p').text

        # condition if Category is none signal no "Category is available" else  continu to scrap
        if soup.find('ul', {'class': 'breadcrumb'}).find_all('li')[2].text.strip('\n') is None:
            book_review_scraper['category'] = 'No Category is available'
        else:
            book_review_scraper['category'] = soup.find('ul', {'class': 'breadcrumb'}).find_all('li')[2].text.strip('\n')
            #default value of star-rating
            book_review_scraper['review_star_rating'] = 0
        product_book = soup.find('p', {'class': 'instock availability'}).find_all('p')

        for infos in product_book:
            # if star rating is none in class [0] pass else take the next "p" in  the class[1]
            if infos['class'][0] != 'star-rating':
                pass
            else:
                book_review_scraper['review_star_rating'] = infos['class'][1]

        book_review_scraper['image_url'] = urljoin(req.url, soup.find_all('img')[0]['src'])
        print(book_review_scraper, '\n\n')
        return book_review_scraper


# définition of a fonction which will look for the next page
def get_next_page(url, soup):

    #if the research is not none création of a new url
    if soup.find('li', {'class': 'next'}) is not None:
        next_button = soup.find('li', {'class': 'next'}).find('a')['href']
        #création of the new url with the next button
        new_url = urljoin(url, next_button)
        return new_url

        #else no next page
    else:
        return None


# définition of the fonction navigate
# looking for books lists and extract informations in each page
def navigate(page_url):

    books_info = []
    # condition
    while page_url is not None:
        books_url = []
        req = requests.get(page_url)
        if req.ok:
            # déf soup object
            soup = BeautifulSoup(req.text, 'lxml')
            # looking for books list through class
            books_lis = soup.find_all('li', {'class': "col-xs-6 col-sm-4 col-md-3 col-lg-3"})
            # looking for the url of books list and find the ahref markers
            for books_li in books_lis:
                books_url.append(books_li.find('a')['href'])
            # looking for books informations through books
            for book_url in books_url:
                url = urljoin(page_url, book_url)
                book_info = extraction(url)
                books_info.append(book_info)
            # then  find the next page if there is one
            page_url = get_next_page(page_url, soup)

    return books_info


# définition of the folders creation
def folder_creation(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print('ERROR while trying to create :' + directory)


# définition of the fonction which will load the book's picture
def download_image_product(img_url, book_title, category):
    req = requests.get(img_url)
    if req.ok:

        with open("books_images\\" + category + "\\" + book_title + '.jpg', 'wb') as f_image:
            f_image.write(req.content)
            # f_image.close()


# définition of the fonction will tranform and write the books informations into CSV and jpg
def write_file_to_jpg_csv(books_info):
    rows = []
    header = []
    if len(header) < 1:
        for keys in books_info[0]:
            header.append(keys)

    file_title = books_info[0]['category']
    # loading pictures from each book
    for book_info in books_info:
        download_image_product(book_info['image_url'], (book_info['universal_product_code']), book_info['category'])
        rows.append(book_info)
    # write books infos into csv
    with open("books_info\\" + file_title + '.csv', 'w', encoding="utf-8-sig", newline="") as f_output:
        fieldnames = header
        writer = csv.DictWriter(f_output, fieldnames)
        writer.writeheader()
        writer.writerows(books_info)




#définition of the fonction which will look for books from catégories through pages
def books_infos_through_categories(li):
    req = requests.get(li)
    if req.ok:
        # définition of the soup object
        soup = BeautifulSoup(req.text, 'lxml')
        categories = soup.find('ul', {'class': 'nav nav-list'}).find('ul').find_all('li')
        for category in categories:
            #research markers ahref through the list to look for books from categories
            category_li = urljoin(li, category.find('a')['href'])
            #ajout successif des books infos au travers des categories
            books_info = navigate(category_li)
            # creation of the different folders
            folder_creation("books_images\\" + books_info[0]['category'])
            # write the different files into csv and jpg
            write_file_to_jpg_csv(books_info)






if __name__ == '__main__':
    folder_creation('./books_images')
    folder_creation('./books_info')
    books_infos_through_categories('https://books.toscrape.com/')









