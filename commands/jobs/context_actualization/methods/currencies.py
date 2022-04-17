import string

import investpy

USD_ASSET_NAME = 'USD'


def get_currency_price(currency_cross: string) -> float:
    return 1 if currency_cross == USD_ASSET_NAME \
        else investpy.get_currency_cross_information(currency_cross=f'{currency_cross}/USD')['Open'].values[0]
