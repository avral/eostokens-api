import requests
import time
import itertools

from django.utils.dateparse import parse_datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.core.cache import cache
from eospy.cleos import Cleos

from django.db.models import Q
from eostokens_api.settings import HYPERION_URL, DEX_CONTRACTS

from history_api.models import BuyOrder, SellOrder, Market, PriceHistory
from history_api.utils import get_aware_datetime


ZERO = Decimal('0')
DEX_ACTIONS = ['sellreceipt', 'buyreceipt', 'sellmatch',
               'buymatch', 'cancelbuy', 'cancelsell', 'clean']


def handle_market(quote, base, contract):
    q = Market.objects.filter(contract=contract)

    if not q.exists():
        # First market on contract
        Market.objects.create(contract=contract,
                              market_id=0,
                              quote=quote,
                              base=base)
    else:
        if not q.filter(quote=quote, base=base).exists():
            market_id = q.order_by('-market_id').first().market_id + 1
            Market.objects.create(market_id=market_id,
                                  quote=quote,
                                  base=base,
                                  contract=contract)


def save_price_history(quote, base, time):
    price = None

    # sell_orders = SellOrder.objects.filter(quote=quote, base=base)
    buy_orders = BuyOrder.objects.filter(quote=quote, base=base)

    if buy_orders.exists():
        price = buy_orders.order_by('price').last().price
    # Only by buy price
    # elif sell_orders.exists():
    #    price = sell_orders.order_by('price').first().price

    if price is not None:
        p = PriceHistory.objects.create(price=price,
                                        quote=quote,
                                        base=base,
                                        time=time)

        print('save some price', p)


def handle_action(act, contract):
    data = act['data']

    #if act['name'] in ['sellmatch', 'buymatch']:
    #    data = act['data']['record']

    #    type = act['name']
    #    bidder = data['bidder']
    #    asker = data['asker']
    #    bid = data['bid']
    #    ask = data['ask']
    #    price = data['unit_price']
    #    print(data)

    #    pass

    if act['name'] == 'cancelbuy':
        market = Market.objects.get(contract=contract, market_id=int(data['market_id']))
        BuyOrder.objects.filter(account=data['executor'], quote=market.quote, order_id=data['order_id']).delete()

        save_price_history(market.quote, market.base, time=act['timestamp'])

    if act['name'] == 'cancelsell':
        market = Market.objects.get(contract=contract, market_id=int(data['market_id']))
        SellOrder.objects.filter(account=data['executor'], quote=market.quote, order_id=data['order_id']).delete()

        save_price_history(market.quote, market.base, time=act['timestamp'])

    if act['name'] == 'clean':
        market_id = int(act['data']['market_id'])

        market = Market.objects.get(market_id=market_id)
        market.delete()

        SellOrder.objects.filter(quote=market.quote, base=market.base).delete()
        BuyOrder.objects.filter(quote=market.quote, base=market.base).delete()
        PriceHistory.objects.filter(quote=market.quote, base=market.base).delete()

    if act['name'] == 'sellmatch':
        data = act['data']['record']

        bid = data['bid'].split(' ')
        ask = data['ask'].split(' ')

        order = BuyOrder.objects.filter(quote=bid[1], base=ask[1], price=data['unit_price']).order_by('time').first()
        order.ask -= Decimal(bid[0])
        order.bid -= Decimal(ask[0])
        order.save()

        if order.ask == ZERO or order.bid == ZERO:
            order.delete()
        else:
            order.save()

        save_price_history(bid[1], ask[1], time=act['timestamp'])

    if act['name'] == 'buymatch':
        data = act['data']['record']

        bid = data['bid'].split(' ')
        ask = data['ask'].split(' ')

        order = SellOrder.objects.filter(quote=ask[1], base=bid[1], price=data['unit_price']).order_by('time').first()
        order.ask -= Decimal(bid[0])
        order.bid -= Decimal(ask[0])

        if order.ask == ZERO or order.bid == ZERO:
            order.delete()
        else:
            order.save()

        save_price_history(ask[1], bid[1], time=act['timestamp'])

    if act['name'] == 'sellreceipt':
        data = act['data']['sell_order']

        bid = data['bid'].split(' ')
        ask = data['ask'].split(' ')

        handle_market(bid[1], ask[1], contract)

        SellOrder.objects.create(
            account=data['account'],
            quote=bid[1],
            base=ask[1],
            bid=bid[0],
            ask=ask[0],
            price=data['unit_price'],
            order_id=data['id'],
            time=act['timestamp']
        )

        save_price_history(bid[1], ask[1], time=act['timestamp'])

    if act['name'] == 'buyreceipt':
        data = act['data']['buy_order']

        bid = data['bid'].split(' ')
        ask = data['ask'].split(' ')

        handle_market(ask[1], bid[1], contract)

        BuyOrder.objects.create(
            account=data['account'],
            quote=ask[1],
            base=bid[1],
            bid=bid[0],
            ask=ask[0],
            price=data['unit_price'],
            order_id=data['id'],
            time=act['timestamp']
        )

        save_price_history(ask[1], bid[1], time=act['timestamp'])


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        for contract in itertools.cycle(DEX_CONTRACTS.values()):
            skip = cache.get(f'hyperion_skip_point__{contract}', 0)
            print(f'scan hyperion_skip_point__{contract} from', skip)

            try:
                r = requests.get(f'{HYPERION_URL}/history/get_actions',
                                 {'account': contract,
                                  'skip': skip, 'sort': '1',
                                  'limit': '1000'}).json()
            except Exception as err:
                print('request hyperion error', err)
                continue

            for act in r['actions']:
                timestamp = get_aware_datetime(act['@timestamp'])
                act = act['act']
                act['timestamp'] = timestamp

                skip += 1

                cache.set(f'hyperion_skip_point__{contract}', skip)

                if act['name'] not in DEX_ACTIONS:
                    continue

                handle_action(act, contract)

            time.sleep(5)
