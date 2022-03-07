import pandas as pd
import datetime as dt

tweets ={ 1: {'date': dt.datetime(2021,9,6,17,33),
        'link': "https://twitter.com/nayibbukele/status/1435023474494410753?s=20&t=0FdsMFhvyz1zGrAWAiKMPQ",
        'num_coins': 200,
        },
        2: {'date': dt.datetime(2021,9,19,22,53) ,
            'link': "https://twitter.com/nayibbukele/status/1439815012642611203?s=20&t=0FdsMFhvyz1zGrAWAiKMPQ",
            'num_coins': 150,
        },
        3: {'date': dt.datetime(2021,10,27,14,40),
            'link': "https://twitter.com/nayibbukele/status/1453461587948445697?s=20&t=0FdsMFhvyz1zGrAWAiKMPQ",
            'num_coins': 420,
        },
        4: {'date': dt.datetime(2021,11,26,12,57),
            'link': "https://twitter.com/nayibbukele/status/1464307422793715716?s=20&t=0FdsMFhvyz1zGrAWAiKMPQ",
            'num_coins': 100,
        },
        5: {'date': dt.datetime(2021,12,3,23,19),
            'link': "https://twitter.com/nayibbukele/status/1467000621354135555?s=20&t=0FdsMFhvyz1zGrAWAiKMPQ",
            'num_coins': 150,
        },
        6: {'date': dt.datetime(2022,1,21,16,18),
            'link': "https://twitter.com/nayibbukele/status/1484651539587289091?s=20&t=0FdsMFhvyz1zGrAWAiKMPQ",
            'num_coins': 410,
        }
}

returns = []