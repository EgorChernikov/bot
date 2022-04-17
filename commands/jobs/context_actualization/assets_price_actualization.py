import string
from datetime import datetime

from telegram.ext import CallbackContext

from commands.jobs.context_actualization.methods.currencies import get_currency_price, USD_ASSET_NAME
from context.base import Session
from context.entities.asset import AssetType, Asset

CURRENCIES_ASSETS = [USD_ASSET_NAME, 'RUB', 'EUR']


def __actualize_asset_price(asset_name: string, asset_type: AssetType, method):
    price_usd: float = method(asset_name)

    session = Session()
    asset = session.query(Asset).filter_by(name=asset_name).first()

    if asset is None:
        asset = Asset(asset_type, asset_name, price_usd, datetime.now())
        session.add(asset)
    else:
        asset.price_usd = price_usd
        asset.last_price_update_datetime = datetime.now()

    session.commit()
    session.close()


def actualize_assets_price(context: CallbackContext):
    for asset_name in CURRENCIES_ASSETS:
        __actualize_asset_price(asset_name, AssetType.CURRENCY, get_currency_price)
