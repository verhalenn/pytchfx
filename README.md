Pytchfx 
=======

A slower scraper for a more effecient database.

Using the Pitchrx package I didn't like using

Getting Started 
---------------

Pytchfx requires an sqlalchemy engine to function. To figure out how to
configure an sqlalchemy engine go to this
[link](http://docs.sqlalchemy.org/en/latest/core/engines.html).

Below is a simple example that creates a database in memory from games
between 2016/06/06 and 2016/06/09. Dates should be in the format
YYYY/MM/DD.

```python
from pytchfx import scrape
from sqlalchemy import create_engine

engine = create_engine("sqlite://")
scrape(start='2016/06/06', end='2016/06/09', engine=engine)
```
