# Generated by Django 3.2.9 on 2023-01-14 16:41

from django.db import migrations
from Clear.models import Boroughs


def InsertBoroughs(apps, schema_editor):
    Boroughs.objects.create(code=1, OutwardName="Barking and Dagenham", ApiName="barkinganddagenham")
    Boroughs.objects.create(code=2, OutwardName="Barnet", ApiName="barnet")
    Boroughs.objects.create(code=3, OutwardName="Bexley", ApiName="bexley")
    Boroughs.objects.create(code=4, OutwardName="Brent", ApiName="brent")
    Boroughs.objects.create(code=5, OutwardName="Bromley", ApiName="bromley")
    Boroughs.objects.create(code=6, OutwardName="Camden", ApiName="camden")
    Boroughs.objects.create(code=7, OutwardName="City of London", ApiName="cityoflondon")
    Boroughs.objects.create(code=8, OutwardName="Croydon", ApiName="croydon")
    Boroughs.objects.create(code=9, OutwardName="Ealing", ApiName="ealing")
    Boroughs.objects.create(code=10, OutwardName="Enfield", ApiName="enfield")
    Boroughs.objects.create(code=11, OutwardName="Greenwich", ApiName="greenwich")
    Boroughs.objects.create(code=12, OutwardName="Hackney", ApiName="hackney")
    Boroughs.objects.create(code=13, OutwardName="Hammersmith and Fulham", ApiName="hammersmithandfulham")
    Boroughs.objects.create(code=14, OutwardName="Haringey", ApiName="haringey")
    Boroughs.objects.create(code=15, OutwardName="Harrow", ApiName="harrow")
    Boroughs.objects.create(code=16, OutwardName="Havering", ApiName="havering")
    Boroughs.objects.create(code=17, OutwardName="Hillingdon", ApiName="hillingdon")
    Boroughs.objects.create(code=18, OutwardName="Hounslow", ApiName="hounslow")
    Boroughs.objects.create(code=19, OutwardName="Islington", ApiName="islington")
    Boroughs.objects.create(code=20, OutwardName="Kensington and Chelsea", ApiName="kensingtonandchelsea")
    Boroughs.objects.create(code=21, OutwardName="Kingston", ApiName="kingston")
    Boroughs.objects.create(code=22, OutwardName="Lambeth", ApiName="lambeth")
    Boroughs.objects.create(code=23, OutwardName="Lewisham", ApiName="lewisham")
    Boroughs.objects.create(code=24, OutwardName="Merton", ApiName="merton")
    Boroughs.objects.create(code=25, OutwardName="Newham", ApiName="newham")
    Boroughs.objects.create(code=26, OutwardName="Redbridge", ApiName="redbridge")
    Boroughs.objects.create(code=27, OutwardName="Richmond", ApiName="richmond")
    Boroughs.objects.create(code=28, OutwardName="Southwark", ApiName="southwark")
    Boroughs.objects.create(code=29, OutwardName="Sutton", ApiName="sutton")
    Boroughs.objects.create(code=30, OutwardName="Tower Hamlets", ApiName="towerhamlets")
    Boroughs.objects.create(code=31, OutwardName="Waltham Forest", ApiName="walthamforest")
    Boroughs.objects.create(code=32, OutwardName="Wandsworth", ApiName="wandsworth")
    Boroughs.objects.create(code=33, OutwardName="Westminster", ApiName="westminster")


class Migration(migrations.Migration):

    dependencies = [
        ('Clear', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(InsertBoroughs),
    ]