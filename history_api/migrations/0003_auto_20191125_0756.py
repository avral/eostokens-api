# Generated by Django 2.2.7 on 2019-11-25 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('history_api', '0002_auto_20191117_0618'),
    ]

    operations = [
        migrations.CreateModel(
            name='Trades',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=10, null=True)),
                ('bidder', models.CharField(max_length=12, null=True)),
                ('asker', models.CharField(max_length=12, null=True)),
                ('bid', models.CharField(max_length=20, null=True)),
                ('ask', models.CharField(max_length=20, null=True)),
                ('price', models.BigIntegerField(default=0, null=True)),
                ('quote', models.CharField(max_length=300, null=True)),
                ('base', models.CharField(max_length=300, null=True)),
                ('time', models.DateTimeField(null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='buyorder',
            name='order_id',
            field=models.BigIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='buyorder',
            name='price',
            field=models.BigIntegerField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='market',
            name='market_id',
            field=models.BigIntegerField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='pricehistory',
            name='price',
            field=models.BigIntegerField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='sellorder',
            name='order_id',
            field=models.BigIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='sellorder',
            name='price',
            field=models.BigIntegerField(default=0, null=True),
        ),
    ]