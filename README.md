Pytchfx 
=======

A PITCHf/x scraper written in python.

Getting Started 
---------------

Pytchfx requires an SQLAlchemy engine to function. Instructions on how to configure an SQLAlchemy engine can be found here.
[link](http://docs.sqlalchemy.org/en/latest/core/engines.html).

Below is a simple example that creates a database from games
between 2016/06/06 and 2016/06/09 and places it in memeory. Dates should be in the format
'YYYY/MM/DD'.

```python
from pytchfx import scrape
from sqlalchemy import create_engine

engine = create_engine("sqlite://")
scrape(start='2016/06/06', end='2016/06/09', engine=engine)
```

You can find the meaning behind each column [here](docs/table_scheme.md).

Built With:
-----------

* [Requests](https://2.python-requests.org//en/master/)
* [Pandas](https://pandas.pydata.org/)
* [SQLAlchemy](https://www.sqlalchemy.org/)
* [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
