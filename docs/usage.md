As seen on the getting started page.

Getting Started
---------------

Pytchfx requires an sqlalchemy engine to function. Instructions on how to configure an sqlalchemy engine can be found here.
[link](http://docs.sqlalchemy.org/en/latest/core/engines.html).

Below is a simple example that creates a database in memory from games
between 2016/06/06 and 2016/06/09. Dates should be in the format
'YYYY/MM/DD'.

```python
from pytchfx import scrape
from sqlalchemy import create_engine

engine = create_engine("sqlite://")
scrape(start='2016/06/06', end='2016/06/09', engine=engine)
```

Update Function
---------------

As well there is a simple update function. Taking that same database we
had before let's assume the date today is 2016/06/12. By running.

```python
from pytchfx import update
from sqlalchemy import create_engine

engine = create_engine("sqlite://")
update(engine)
```

It will update the database to 2016/06/11. So it will have all the PITCHf/x
data from 2016/06/06 to 2016/06/11. The reason it doesn't include today's
date in the update is because if there is game going on while you are updating
you may cause problems the database that would be a large pain to clean
later.

This function is especially useful with crontab. For instance if I put
this into a file called update_database.py. I could setup my crontab as

```bash
0 4 * * * python ~/update_database.py
```

This will automatically update the databse at 4 am everymorning. Assuming
that your computer or server is always on.