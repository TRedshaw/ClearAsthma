from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime
import requests
import xml.etree.ElementTree as ET
import json
import geopandas as gpd
import random


class AppUser(AbstractUser):
    """
    This model creates the table to store all records of users. It extends the Django AbstractUser default user table
    as we have custom fields. It contains method relating to updating the table such as updating current borough.
    """
    # CASCADE ensures that if a user is deleted, it deletes all things related to it
    # dob in form YYYY-MM-DD
    dob = models.DateField(default=datetime.date.today)

    # PROTECTs the deletion of a UserProfile if a Borough is tried to be deleted
    current_borough = models.ForeignKey('Boroughs', on_delete=models.PROTECT, related_name='current_users', null=True)

    home_borough = models.ForeignKey('Boroughs', on_delete=models.PROTECT, related_name='home_users', null=True)
    work_borough = models.ForeignKey('Boroughs', on_delete=models.PROTECT, related_name='work_users', null=True)
    other_borough = models.ForeignKey('Boroughs', on_delete=models.PROTECT, related_name='other_users', null=True)

    pollution_limit = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])

    # Consent to allowing us to store their medical information.
    consent = models.BooleanField()

    # Setting required fields so that the register form knows that these need to be filled in order to create a user.
    REQUIRED_FIELDS = ['dob', 'pollution_limit', 'consent']

    class Meta:
        """ Our Metadata classes allow us to set data for the class such as its viewable name. """
        verbose_name = 'App User'
        verbose_name_plural = 'App Users'
        ordering = ['id']

    def __str__(self):
        return self.username

    def set_new_current_borough(current_user, borough_id):
        app_user = AppUser.objects.get(pk=current_user.id)
        borough = Boroughs.objects.get(id=borough_id)
        app_user.current_borough_id = borough.id
        app_user.save()

    def quick_set_current_location(self):
        # TODO For when they choose just work or other or home it gives them the pollution level by clicking
        #  button without having to enter their postcode

        # eg. if work clicked, then take the work location id from the userLocations table and insert into the current
        # location field in this table (for example)
        pass


    def add_location(self):
        # TODO Create code to add a location
        pass


class UserInhaler(models.Model):
    """
    This model contains all records relating a user to an inhaler. This is to normalise the database such that we can
    relate user_id to inhaler_id, and store each instances number of puffs per day etc. It contains methods to reset
    the daily puff count each day, as well as increment puffs today and decrease puffs remaining.
    """

    # models.PROTECT works so if a user tries to delete an 'Inhaler' record (the one in quotations) then it wont let you
    # models.CASCADE will delete all related UserInhalers if a UserProfile (user) is deleted

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_inhaler', null=False)
    inhaler = models.ForeignKey('Inhalers', on_delete=models.PROTECT, related_name='inhaler_user', null=False)
    puffs_today = models.IntegerField(default=0)
    puffs_remaining = models.IntegerField(null=False)
    puffs_per_day = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)  # attributes time

    class Meta:
        verbose_name = 'User Inhaler'
        verbose_name_plural = 'Users Inhalers'
        ordering = ['id']

    def __str__(self):
        return_string = str(self.user_id) + " with " + str(self.inhaler.name)
        return return_string

    def add_inhaler(self):
        # TODO Complete
        pass

    # To reset puffs today to zero every day
    def get_puffs_today(self):
        today_date = datetime.date.today()
        if self.updated_at.strftime('%Y-%m-%d') != str(today_date):
            self.puffs_today = 0
            self.save()


    def delete_inhaler(self):
        # TODO Complete
        pass

    # To log an inhaler usage.
    def log_puff(user_inhaler_id):
        # Get the record where the user_inhaler_id matches that of the one on the site
        user_inhaler = UserInhaler.objects.get(pk=user_inhaler_id)
        # Only allow a puff to be logged if they have puffs remaining
        if user_inhaler.puffs_remaining > 0:
            # Increment the puffs today field for the current record
            user_inhaler.puffs_today += 1
            # Decrease the puffs remaining field
            user_inhaler.puffs_remaining -= 1
            # Update the table
            user_inhaler.save()
            return 1
        return None


class Inhalers(models.Model):
    """
    Contains all inhaler types / their names and has associated ID's.
    """

    name = models.CharField(max_length=64)

    class Meta:
        verbose_name = 'Inhaler'
        verbose_name_plural = 'Inhalers'
        ordering = ['name']


class PollutionLevelInfo(models.Model):
    """
    A model where pollution level limits and their associated warnings are stored.
    """
    band = models.CharField(max_length=6)
    lower_bound = models.IntegerField()
    upper_bound = models.IntegerField()
    general_description = models.CharField(max_length=512)
    risk_description = models.CharField(max_length=512)

    class Meta:
        verbose_name = 'Pollution Level Info'
        verbose_name_plural = 'Pollution Level Info'
        ordering = ['id']

    def __str__(self):
        return self.band


class PollutionLevels(models.Model):
    """
    All boroughs' pollution levels are stored here, with each borough being related by a foreign key.
    """
    # TODO will need to edit at a later date to accomodate for different pollutants
    borough = models.ForeignKey('Boroughs', on_delete=models.CASCADE, related_name='borough_pollution', null=False)
    pollution_level = models.IntegerField(help_text="Overall Pollution Level")
    pollution_level_no2 = models.IntegerField(help_text="NO2 Pollution Level")
    pollution_level_o3 = models.IntegerField(help_text="O3 Pollution Level")
    pollution_level_so2 = models.IntegerField(help_text="SO2 Pollution Level")
    pollution_level_pm10 = models.IntegerField(help_text="PM10 Particulate")
    pollution_level_pm25 = models.IntegerField(help_text="PM25 Particulate")
    pollution_level_pm2_5 = models.IntegerField(help_text="PM2.5 Particulate")
    pollution_date = models.DateField(default=datetime.date.today)

    # The current flag will indicate the record that has the current pollution level for a specific region
    # (True = Current, False (0) = Previous). This allows us to build a history of pollution levels.
    current_flag = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Pollution Levels'
        verbose_name_plural = 'Pollution Levels'
        ordering = ['borough_id']

    def __str__(self):
        return_string = "Level " + str(self.pollution_level) + "@" + str(self.borough_id)
        return return_string

    def update_pollution_levels(self, location):   
        url = ''
        url += 'https://api.erg.ic.ac.uk/AirQuality/Hourly/MonitoringIndex/GroupName='
        borough = location
        url += location
        response = requests.get(url)
        root = ET.fromstring(response.content)
                
        total=0
        number=0
        properties_dict = {}
        pollutiontypes={}
        objects=[]

        for child in root.iter('*'):
            if child.tag == 'Species':
                pollutiontypes[child.attrib['SpeciesCode']]=child.attrib['AirQualityIndex']
                total += int(child.attrib['AirQualityIndex'])
                number += 1

        obj=PollutionLevels()
        for key in pollutiontypes:
            speciesname='pollution_level'+key.lower()
            obj.speciesname = pollutiontypes[key]
        obj.pollution_level = total/number
        obj.current_flag = True

        import sqlite3

        # Create a SQL connection to our SQLite database
        con = sqlite3.connect("db.sqlite3")
        cur = con.cursor()

        # Return all results of query
        cur.execute('SELECT code FROM Clear_boroughs WHERE ApiName=location')
        obj.borough_id=cur.fetchall()
        # Be sure to close the connection
        cur.execute('SELECT OutwardName FROM Clear_boroughs WHERE ApiName=location')
        location_full_name=cur.fetchall()
        con.close()

        objects.append(obj)
        PollutionLevels.bulk_create(objects)


        CURRENT_GEOJSON_FILE = 'london_boroughs.json'
        UPDATED_GEOJSON_FILE = 'updated_london_boroughs.json'
                # Read current geojson file into a GeoDataFrame from gpd
        boroughs = gpd.read_file(CURRENT_GEOJSON_FILE)
                # Add a new columns for features like color or pollution level
        boroughs.insert(loc=1,column='obj.pollution_level',value=0)
        boroughs.insert(loc=2,column='fill',value=0)

                # Fill those newly created columns
        for i in range(len(boroughs.index)):
            if boroughs.name[i] == location_full_name:
                boroughs.overall_pollution_level[i]= obj.pollution_level
                boroughs.fill[i] = "#%06x" % random.randint(0, 0xFFFFFF)
            else:
                boroughs.obj.pollution_level[i]= 0
                boroughs.fill[i] = "000000"
        # Write back updated GeoDataFrame to geojson file
        boroughs.to_file(UPDATED_GEOJSON_FILE, driver="GeoJSON")
        pass


class Boroughs(models.Model):
    code = models.IntegerField()
    OutwardName = models.CharField(max_length=128)
    ApiName = models.CharField(max_length=128)

    class Meta:
        verbose_name = 'Borough'
        verbose_name_plural = 'Boroughs'
        ordering = ['OutwardName']

    def __str__(self):
        return self.OutwardName


