## Initialization

    $ python manage.py loaddata logs accounts configs sources
    $ python manage.py loaddata cog01 cog02 cog03 cog04 cog05 cog06 cog07 cog08 cog09 cog10 cog11 cog12 cog13 cog14
    $ python manage.py loaddata 2018h1 2018h2 mp-2018h1 mp-2018h2 2019h1 mp-2019h1

## Code Naming Convention:

1. config: COG
2. chart: CHT
3. log type: LOT


## Config Products Primary Key Distribution:

#### Config.code: AbstractProduct.id

1. COG01: 1 - 10000
2. COG02: 10001 - 20000
3. COG03: 20001 - 30000
4. COG04: 30001 - 40000
5. COG05: 40001 - 50000
6. COG06: 50001 - 60000
7. COG07: 60001 - 70000
8. COG08: 70001 - 80000
9. COG09: 80001 - 90000
10. COG010: 90001 - 100000
11. COG011: 100001 - 110000
12. COG012: 110001 - 120000
13. COG013: 120001 - 130000
14. COG014: 130001 - 140000

## Config Source Primary Key Distribution:

#### App.label: Source.id

1. rices: 1 - 10000
2. crops: 10001 - 20000
3. fruits: 20001 - 30000
4. flowers: 30001 - 40000
5. hogs: 40001 - 50000
6. rams: 50001 - 60000
7. ...
