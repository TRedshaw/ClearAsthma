15th January 2023
How to locally use Clear:
    - Clone the GitHub Repository locally in your prefered editor by creating a 'New Project from VCS' or quivalent
    - Open Terminal either in the editor, or on your computer and navigate to your current working directory
        - Run 'py manage.py migrate'
        - Run 'py -m venv env' - if propmted to chose this as an environment, select yes - this ensure everything you install is uptodate and contained to this project folder only
        - Navigate to the 'Scripts' folder inside the venv, and run ' .\activate'
        - Navigate back out to the ClearAsthma folder
        - Install the following modules using 'pip install #insert module here#'
            modules:
            - requests
            - django
            - geopandas
            - json
            - xml.etree.ElementTree
        - Now you are ready to run the code! In Terminal still, you can run 'py manage.py runserver'
        - Click the link the terminal displays, and add '/clear/pollution' at the end to access the pollution page for example



CODE USED TO SETUP THE PROJECT FRAMEWORK: 
Bootstrap Versions Documentation: https://getbootstrap.com/docs/versions/

Django Documentation: https://docs.djangoproject.com/en/4.1/

Bootstrap Components eg menu bar / button: https://getbootstrap.com/docs/4.0/components/alerts/

Fonts: https://fontawesome.com

Youtube Tutorials Series: https://www.youtube.com/watch?v=qDwdMDQ8oX4&list=PL-osiE80TeTtoQCKZ03TU5fNfx2UY6U4p&index=3

Deployment Documentation: https://devcenter.heroku.com/categories/python-support