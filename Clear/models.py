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
    @classmethod
    def log_puff(cls, user_inhaler_id):
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

    def update_pollution_levels():   
        url = 'https://api.erg.ic.ac.uk/AirQuality/Hourly/MonitoringIndex/GroupName=London/Json'
        response = requests.get(url)
        data = response.json()
        #initialise all values to 0 
        for local_authority in data['HourlyAirQualityIndex']['LocalAuthority']:

            borough_pollution_max = 0
            borough_pollution_count = 0
            borough_pollution_sum = 0
            borough_pollution_average = 0

            pollution_readings = {
                'SO2': {'sum': 0, 'count': 0, 'average': 0},
                'NO2': {'sum': 0, 'count': 0, 'average': 0},
                'O3': {'sum': 0, 'count': 0, 'average': 0},
                'PM250': {'sum': 0, 'count': 0, 'average': 0},
                'PM10': {'sum': 0, 'count': 0, 'average': 0},
                'PM25': {'sum': 0, 'count': 0, 'average': 0}
            }

            try:
                borough = Boroughs.objects.filter(code=local_authority['@LocalAuthorityCode']).first()

                for site in local_authority['Site']:
                    site_pollutions_level = 0
                    try:
                        for species in site['Species']:
                            species_code = species['@SpeciesCode']
                            pollution_level = int(species['@AirQualityIndex'])
                            pollution_readings[species_code]['sum'] += pollution_level
                            pollution_readings[species_code]['count'] += 1
                            pollution_readings[species_code]['average'] = pollution_readings[species_code]['sum'] / pollution_readings[species_code]['count']

                            if pollution_level > borough_pollution_max:
                                borough_pollution_max = pollution_level

                            borough_pollution_sum += pollution_level
                            borough_pollution_count += 1

                            # Average will include 0 value results from sitees but we don't assume that
                            # if there's no entry for a Site, that the value would be 0
                            # So readings of 0 affect the average, missing values don't
                            borough_pollution_average = round(borough_pollution_sum/borough_pollution_count)
                            # Debugging the average calculation
                            # print(borough.id, borough.OutwardName, borough_pollution_sum, borough_pollution_count, borough_pollution_max, borough_pollution_average, pollution_level)

                    # Some objects have Species as a string
                    except TypeError:
                        pass

                if borough != None:
                    PollutionLevels.objects.filter(borough_id=borough.id).update(current_flag=0)

                    PollutionLevels.objects.create(
                        pollution_level=borough_pollution_average,
                        pollution_level_no2=pollution_readings['NO2']['average'],
                        pollution_level_so2=pollution_readings['SO2']['average'],
                        pollution_level_o3=pollution_readings['O3']['average'],
                        # Data doesn't have PM250
                        pollution_level_pm25=pollution_readings['PM250']['average'],
                        pollution_level_pm10=pollution_readings['PM10']['average'],
                        pollution_level_pm2_5=pollution_readings['PM25']['average'],
                        borough_id=borough.id,
                        current_flag = 1,
                        pollution_date=datetime.date.today()
                    )
            except KeyError:
                pass

    @classmethod
    def get_borough_map(cls):
        boroughs = Boroughs.objects.all()
        for borough in boroughs:

            CURRENT_GEOJSON_FILE = 'london_boroughs.json'
            # Read current geojson file into a GeoDataFrame from gpd
            bor = gpd.read_file(CURRENT_GEOJSON_FILE)
            bor.insert(loc=1, column='color', value=0)

            for i in range(len(bor.index)):
                bor.color[i] = "#%06x" % random.randint(0, 0xFFFFFF)
                # print(bor.name[i], borough)
                # if bor.name[i] == borough:
                #     bor.color[i] = "#%06x" % random.randint(0, 0xFFFFFF)
                # else:
                #     bor.color[i] = "000000"
        return bor.to_json()

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