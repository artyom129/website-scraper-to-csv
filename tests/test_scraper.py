from bs4 import BeautifulSoup

from website_scraper_to_csv import Book, parse_books_from_page, remove_duplicates


def test_parse_books_from_page():
    html = """
    <article class="product_pod">
      <p class="star-rating Three"></p>
      <h3><a href="catalogue/example_1/index.html" title="Example Book">Example</a></h3>
      <p class="price_color">£19.99</p>
      <p class="availability">In stock</p>
    </article>
    """
    books = parse_books_from_page(BeautifulSoup(html, "html.parser"))

    assert len(books) == 1
    assert books[0].title == "Example Book"
    assert books[0].price == "£19.99"
    assert books[0].availability == "In stock"
    assert books[0].rating == "Three"
    assert books[0].product_url.endswith("catalogue/example_1/index.html")


def test_remove_duplicates_by_product_url():
    first = Book("A", "1", "In stock", "Five", "https://example.com/a")
    duplicate = Book("A copy", "2", "In stock", "Four", "https://example.com/a")
    second = Book("B", "3", "In stock", "Three", "https://example.com/b")

    result = remove_duplicates([first, duplicate, second])

    assert result == [first, second]
