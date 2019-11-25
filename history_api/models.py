from django.db import models
from django.contrib.postgres.fields import JSONField
# TODO Зарефакторить маркет, создать единую модельку


CURRENCY_TYPES = (
    ('sell', 'sellmatch'),
    ('ETH', 'buymatch')
)


# TODO Подробный парсин ассетов
def default_asset():
    return dict(
        contract='',
        symbol='',
        precision=0
    )


class Trades(models.Model):
    type = models.CharField(max_length=10, null=True)
    bidder = models.CharField(max_length=12, null=True)
    asker = models.CharField(max_length=12, null=True)
    bid = models.CharField(max_length=20, null=True)
    ask = models.CharField(max_length=20, null=True)
    price = models.IntegerField(null=True, default=0)
    quote = models.CharField(max_length=300, null=True)
    base = models.CharField(max_length=300, null=True)
    time = models.DateTimeField(null=True)

    def __str__(self):
        return f'{self.time} | {self.price} ({self.quote}/{self.base})'


class PriceHistory(models.Model):
    price = models.IntegerField(null=True, default=0)
    quote = models.CharField(max_length=300, null=True)
    base = models.CharField(max_length=300, null=True)
    time = models.DateTimeField(null=True)

    # TODO Нужно зарефакторить маркет так что бы можно быль смотреть
    # контракт, пресижн, симбвол бейс и квот

    def __str__(self):
        return f'{self.time} | {self.price} ({self.quote}/{self.base})'


class Market(models.Model):
    market_id = models.IntegerField(default=0, null=True)
    quote = models.CharField(max_length=12)
    base = models.CharField(max_length=12)
    #quote = JSONField(max_length=500, default=default_asset)
    #base = JSONField(max_length=500, default=default_asset)
    contract = models.CharField(max_length=12, null=True)


class SellOrder(models.Model):
    account = models.CharField(max_length=12, null=True)
    quote = models.CharField(max_length=300, null=True)
    base = models.CharField(max_length=300, null=True)

    bid = models.DecimalField('Currency Amount', default=0, null=True, max_digits=19, decimal_places=10)
    ask = models.DecimalField('Currency Amount', default=0, null=True, max_digits=19, decimal_places=10)

    price = models.IntegerField(default=0, null=True)
    time = models.DateTimeField(null=True)

    order_id = models.IntegerField(null=True)

    def __str__(self):
        return f'(SellOrder) {self.account} ask: {self.ask} {self.base} | bid: {self.bid} {self.quote}'


class BuyOrder(models.Model):
    account = models.CharField(max_length=12, null=True)
    quote = models.CharField(max_length=300, null=True)
    base = models.CharField(max_length=300, null=True)

    bid = models.DecimalField('Currency Amount', default=0, null=True, max_digits=19, decimal_places=10)
    ask = models.DecimalField('Currency Amount', default=0, null=True, max_digits=19, decimal_places=10)

    price = models.IntegerField(default=0, null=True)
    time = models.DateTimeField(null=True)
    order_id = models.IntegerField(null=True)

    def __str__(self):
        return f'(BuyOrder) {self.account} ask: {self.ask} {self.quote} | bid: {self.bid} {self.base}'
