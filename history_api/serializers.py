from django.utils.dateformat import format
from django.utils.timezone import now
from datetime import timedelta

from rest_framework import serializers
from history_api.models import Market, PriceHistory


class MarketSerializer(serializers.ModelSerializer):
    change_24_percent = serializers.SerializerMethodField()
    hight_24 = serializers.SerializerMethodField()
    low_24 = serializers.SerializerMethodField()
    last_price = serializers.SerializerMethodField()

    class Meta:
        model = Market
        fields = '__all__'

    def get_hight_24(self, obj):
        q = PriceHistory.objects.filter(
            base=obj.base,
            quote=obj.quote
        )

        date_24_ago = now() - timedelta(days=1)
        hiest_24_price = q.filter(time__gte=date_24_ago).order_by('-price').first()

        if hiest_24_price:
            return hiest_24_price.price
        else:
            return self.get_last_price(obj)

    def get_low_24(self, obj):
        q = PriceHistory.objects.filter(
            base=obj.base,
            quote=obj.quote
        )

        date_24_ago = now() - timedelta(days=1)
        hiest_24_price = q.filter(time__gte=date_24_ago).order_by('price').first()

        if hiest_24_price:
            return hiest_24_price.price
        else:
            return self.get_last_price(obj)

    def get_last_price(self, obj):
        ins = PriceHistory.objects.filter(base=obj.base, quote=obj.quote).order_by('-time').first()

        if ins:
            return ins.price

        return 0


    def get_change_24_percent(self, obj):
        change = 0.0

        q = PriceHistory.objects.filter(base=obj.base, quote=obj.quote)
        last_price = q.last()

        if last_price is None:
            return change

        date_from = now() - timedelta(days=1)
        last_24_history = q.filter(time__gte=date_from).order_by('time').first()

        if last_24_history:
            change = ((last_price.price / last_24_history.price) - 1) * 100

        return round(change, 2)


class PriceHistorySerializer(serializers.ModelSerializer):
    time = serializers.SerializerMethodField()

    class Meta:
        model = PriceHistory
        fields = '__all__'

    def get_time(self, obj):
        return int(format(obj.time, 'U'))
