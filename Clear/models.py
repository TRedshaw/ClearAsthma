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

    # Relate the User to their key Boroughs
    home_borough = models.ForeignKey('Boroughs', on_delete=models.PROTECT, related_name='home_users', null=True)
    work_borough = models.ForeignKey('Boroughs', on_delete=models.PROTECT, related_name='work_users', null=True)
    other_borough = models.ForeignKey('Boroughs', on_delete=models.PROTECT, related_name='other_users', null=True)

    # Store the Pollution Limit for the User
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
        # Get the user object where the ID matches that of the logged-in user
        app_user = AppUser.objects.get(pk=current_user.id)
        # Get the borough where the ID matches that of the borough the user has selected
        borough = Boroughs.objects.get(id=borough_id)
        # Set the current borough id field for the logged-in user to the id of the borough they have selected
        app_user.current_borough_id = borough.id
        # Update the table
        app_user.save()

    def quick_set_current_location(self):
        pass

    def add_location(self):
        pass


class UserInhaler(models.Model):
    """
    This model contains all records relating a user to an inhaler. This is to normalise the database such that we can
    relate user_id to inhaler_id, and store each instances number of puffs per day etc. It contains methods to reset
    the daily puff count each day, as well as increment puffs today and decrease puffs remaining.
    """

    # models.PROTECT works so if a user tries to delete an 'Inhaler' record (the one in quotations) then it wont let you
    # models.CASCADE will delete all related UserInhalers if a UserProfile (user) is deleted
    # The setup of the fields for the user-inhaler relationship database
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_inhaler', null=False)
    inhaler = models.ForeignKey('Inhalers', on_delete=models.PROTECT, related_name='inhaler_user', null=False)
    # Number of puffs used today
    puffs_today = models.IntegerField(default=0)
    # Puffs remaining in the Inhaler
    puffs_remaining = models.IntegerField(null=False)
    # Number of puffs prescribed each day
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
        pass

    # To reset puffs today to zero every day
    def get_puffs_today(self):
        today_date = datetime.date.today()
        if self.updated_at.strftime('%Y-%m-%d') != str(today_date):
            self.puffs_today = 0
            self.save()

    def delete_inhaler(self):
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
    # Set fields for the borough ID (that is a foreign key relating to a borough in the Boroughs table)
    borough = models.ForeignKey('Boroughs', on_delete=models.CASCADE, related_name='borough_pollution', null=False)
    # Create integer fields for all pollutant levels and an overall pollution level
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

    @classmethod
    def update_pollution_levels(cls):
        # Retrieve the current pollution level from the AirQuality API
        url = 'https://api.erg.ic.ac.uk/AirQuality/Hourly/MonitoringIndex/GroupName=London/Json'
        response = requests.get(url)
        # Retrieve the response as JSON
        data = response.json()
        # Loop over the local authorities
        for local_authority in data['HourlyAirQualityIndex']['LocalAuthority']:

            # Reset average statistics for the Borough
            borough_pollution_max = 0
            borough_pollution_count = 0
            borough_pollution_sum = 0
            borough_pollution_average = 0

            # Create an empty dict for storing detailed levels for the Borough
            pollution_readings = {
                'SO2': {'sum': 0, 'count': 0, 'average': 0},
                'NO2': {'sum': 0, 'count': 0, 'average': 0},
                'O3': {'sum': 0, 'count': 0, 'average': 0},
                'PM250': {'sum': 0, 'count': 0, 'average': 0},
                'PM10': {'sum': 0, 'count': 0, 'average': 0},
                'PM25': {'sum': 0, 'count': 0, 'average': 0}
            }

            try:
                # Retrieve the Borough matching the LocalAuthorityCode (we do this here so we can use the Borough in debugging)
                borough = Boroughs.objects.filter(code=local_authority['@LocalAuthorityCode']).first()

                # Loop over all the sensor locations (Sites) for a Borough
                for site in local_authority['Site']:
                    site_pollutions_level = 0
                    try:
                        # Loop over all the pollutant levels measured at the Site
                        for species in site['Species']:
                            # Add the reading for this site / pollutant to the dict for that pollutant
                            # This allows us to average the readings for the same pollutant across multiple
                            # Sites within the same Borough
                            species_code = species['@SpeciesCode']
                            pollution_level = int(species['@AirQualityIndex'])
                            # Add the pollution level at this site
                            pollution_readings[species_code]['sum'] += pollution_level
                            # Increment the number of readings for this pollutant
                            pollution_readings[species_code]['count'] += 1
                            # Calculate the average pollutant level for this pollutant
                            # We do this here because it means we definitely have one reading
                            # If we calculate the average at the end, there may be some pollutants with
                            # 0 readings which will result in a division by 0 error
                            pollution_readings[species_code]['average'] = pollution_readings[species_code]['sum'] / pollution_readings[species_code]['count']

                            # Keep track of the maximum pollution level of any pollutant for the borough (future use)
                            if pollution_level > borough_pollution_max:
                                borough_pollution_max = pollution_level

                            # Add the pollutant level to the total for the Borough
                            borough_pollution_sum += pollution_level
                            # Increment the number of readings for the Borough
                            borough_pollution_count += 1

                            # Average will include 0 value results from sites but we don't assume that
                            # if there's no entry for a Site, that the value would be 0
                            # So readings of 0 affect the average, missing values don't
                            borough_pollution_average = round(borough_pollution_sum/borough_pollution_count)
                            # Debugging the average calculation
                            # print(borough.id, borough.OutwardName, borough_pollution_sum, borough_pollution_count, borough_pollution_max, borough_pollution_average, pollution_level)

                    # Some objects have Species as a string so we catch this error
                    except TypeError:
                        pass

                # Make sure that we have this Borough in our database and update the PollutionLevels if we do
                if borough != None:
                    # Reset the "current" flag on all the existing PollutionLevels for this Borough
                    PollutionLevels.objects.filter(borough_id=borough.id).update(current_flag=0)
                    # Add the new "current" PollutionLevel for this Borough
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
            # Some Local Authorities have no monitoring Sites therefore there is no Site key - catch this error
            except KeyError:
                pass

    @classmethod
    def get_borough_map(cls):
        CURRENT_GEOJSON_FILE = 'london_boroughs.json' #Load the geojspn file
        bor = gpd.read_file(CURRENT_GEOJSON_FILE) # Read current geojson file into a GeoDataFrame from gpd
        bor1=bor.copy() #Save as a copy so we don't get pandas accessing and changing errors
        
        bor1.insert(loc=1, column='color', value=000000) #Insert empty color property in each borough in the file
        current_borough_id=int
        #create a dictionary to access each pollution level's corresponding colour
        colours={0:'#000000', 1:'#27a139', 2:'#27a139', 3:'#27a139', 4:'#f2f21d', 5:'#f2f21d', 6:'#f2f21d', 7:'#e6331c', 8:'#e6331c', 9:'#e6331c', 10:'#ab1df2'}
        #Loop through every borough in the file, find it's borough_id to find the overall pollution level from the database
        for i in range(len(bor1.index)):                    
            current_borough_obj=Boroughs.objects.filter(OutwardName=bor1.name[i]).first()
            #handle NoneType Errors
            if current_borough_obj==None:
                pass
            else:
                current_borough_id=current_borough_obj.id
                
                overall_pollution_level_obj = PollutionLevels.objects.filter(borough_id=current_borough_id, current_flag=1).first()
                if overall_pollution_level_obj==None:
                    pass
                else:
                    overall_pollution_level = overall_pollution_level_obj.pollution_level
                    bor1.color[i] = colours[overall_pollution_level] # assign the colour corresponding to the current pollution level for each borough we looped through
        return bor1.to_json()

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