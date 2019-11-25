from datetime import datetime, timedelta
from collections import defaultdict

from django.utils.dateformat import format
from django.utils import timezone
from django.db.models.functions import TruncDay
from rest_framework.views import APIView
from rest_framework import viewsets, serializers
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Count

from history_api.models import Market, PriceHistory
from history_api.serializers import MarketSerializer, PriceHistorySerializer


ONE_HOUR = 60*60


# TODO Вынести в утилс
PRICE_SCALE = 100000000
PRICE_DIGITS = 8


def human_price(amount):
    return (amount / PRICE_SCALE).toFixed(PRICE_DIGITS)


def t(time):
    return int(format(time, 'U'))


class MarketViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Market.objects.all()
    serializer_class = MarketSerializer
    filterset_fields = ('base', 'quote')


class PriceHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PriceHistory.objects.all()
    serializer_class = PriceHistorySerializer
    filterset_fields = ('base', 'quote')


class ChatrsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        result = []

        q = PriceHistory.objects

        quote = request.GET.get('quote')
        base = request.GET.get('base')

        if quote:
            q = q.filter(quote=quote)
        if base:
            q = q.filter(base=base)

        chunks = {}
        time = q.first().time

        while True:
            time += timedelta(days=1)

            time_str = time.strftime("%Y-%m-%d")

            # TODO Чето для последнего дня не отображает
            if time > timezone.now():
                time -= timedelta(days=1)

                time_str = time.strftime("%Y-%m-%d")
                chunks[time_str] = q.filter(time__year=time.year,
                                            time__month=time.month,
                                            time__day=time.day
                                            ).values('time', 'price')
                break

            chunks[time_str] = q.filter(time__year=time.year,
                                        time__month=time.month,
                                        time__day=time.day
                                        ).values('time', 'price')

        for time, values in chunks.items():
            if not len(values):
                last_item = result[-1]

                result.append({
                    'time': time,
                    'open': last_item['close'],
                    'high': last_item['close'],
                    'low': last_item['close'],
                    'close': last_item['close'],
                    'volume': 0
                })

                continue

            result.append({
                'time': time,
                'open': values.first()['price'],
                'high': max([v['price'] for v in values]),
                'low': min([v['price'] for v in values]),
                'close': values.last()['price'],
                'volume': 0
            })

        return Response(result)
