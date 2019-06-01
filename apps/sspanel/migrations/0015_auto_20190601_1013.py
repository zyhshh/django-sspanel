# Generated by Django 2.2.1 on 2019-06-01 02:13

from django.db import migrations, models
import pendulum


class Migration(migrations.Migration):

    dependencies = [
        ('sspanel', '0014_ssnode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ssnode',
            name='enable',
            field=models.BooleanField(db_index=True, default=True, verbose_name='是否开启'),
        ),
        migrations.CreateModel(
            name='UserCheckInLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.PositiveIntegerField()),
                ('date', models.DateField(db_index=True, default=pendulum.today, verbose_name='记录日期')),
                ('increased_traffic', models.BigIntegerField(default=0, verbose_name='增加的流量')),
            ],
            options={
                'unique_together': {('user_id', 'date')},
            },
        ),
    ]