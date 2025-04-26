from collections import defaultdict
from typing import Any, Callable

import pandas as pd
from prosperity3bt.data import PriceRow, read_day_data
from prosperity3bt.file_reader import PackageResourcesReader


def read_price_data(round_days: list[tuple[int, int]], value_extractor: Callable[[PriceRow], Any]) -> pd.DataFrame:
    file_reader = PackageResourcesReader()

    values_by_product = defaultdict(list)
    for round, day in round_days:
        data = read_day_data(file_reader, round, day, True)

        for timestamp in sorted(data.prices):
            for product, row in data.prices[timestamp].items():
                values_by_product[product].append(value_extractor(row))

    return pd.DataFrame(values_by_product)
