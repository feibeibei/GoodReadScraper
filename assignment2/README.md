# Web Scraper
A web scraping application that scrape book and author information from
GoodReads website and then display through browser.

## Table of Contents
* Requirement
* Usage
* License

## Requirement
Web Scraper requires the following to run:
* BeautifulSoup4
* PyMongo
* networkx
* argparse
* validators
* request
* d3.js
* ajx
* css fontawesome


## Usage
* . operator to specify a field of an object. For example, book.rating_count
* : operator to specify if a field contains search words. For example,
book.book_id:123
* "" operators to specify exact search term. For example, book.image_url:"123"
* AND, OR, and NOT logical operators. For example, book.rating_count: NOT 123
* One-side unbounded comparison operators >, <. For example, book.rating_count: > 123



## License
Paddington is licensed under the [MIT](#) license.  
Copyright &copy; 2021, Fangyi Zhang
