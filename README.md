# Duitama Colegio Project - Web App
These instructions will help you to configure your environment and deploy the web app.  

*Note: These instructions were culled from notes I kept while configuring the various environments and have not been extensively tested*

### Configure Development Environment
**Install and configure the following applications, in order:**  

1. JRE SE 11+
2. Eclipse (JavaScript developer) or preferred IDE
    - Install [PyDev](http://www.pydev.org/updates)
    - (optional) [Change icons]: "C:\Users\<user>\.p2\pool\plugins\<product_folder>"
3. PostgreSQL Database (14)
4. Python 3+ (64-bit win)
5. Git
6. SQL Data Modeler / Developer
    - [Configure Postgres DSN]: Specify hostname: "\<hostname\>/\<database\>?"
    - [Set result set limit]: Specify *ARRAYFETCHSIZE* value in preferences file
7. Heroku CLI

**Configure environment:**
1. Install dependencies using *pip install* in command prompt:
    - Heroku
    - Pylint (optional)
      - ignore common warnings:  *disable=C0114,C0115,C0116,bare-except,no-else-return*

2. Create and activate virtual environment via command prompt:
    - cd \<virtual_envs_dir> (i.e. c:\home\projects\.venv\)
    - python -m venv \<virtual_env_name>
    - \<virtual_env_name>\Scripts\activate.bat  

4. Install application dependencies using *requirements.txt* file in main application's base directory
    - pip install -r \<path_to_requirements_file>

** ***be sure you are in the newly created virtual environment*** *


### Configure Repository (dcp_repo)

  - clone the *[dcprepo]* project
  - install dependencies (ConfigParser)
  - add libraries to project path and configure *src* folders
  - configure *database.ini*
  - configure initial values: *src/load_intiial_data.sql*
  - create new interpreter pointing to correct virtual env (*Scripts/Python.exe*) and set this as the project-specific interpreter
  - set environment variables and restart IDE: 
    - `setx ENV "development"` (valid values: development, test, staging, production)

### Configure Web Application (dcp)

  - clone the *[dcp]* project
  - update environment variables: *.env*
  - specify source directories as such (*lib*, *test*)
  - create new interpreter pointing to correct virtual env (*Scripts/Python.exe*) and set this as the project-specific interpreter
  - configure initial values: *setup.py*
  - [configure SSL]

### Configure Google API  
1. Grant Google Project service account user API access to Google Drive user account (GOOGLE_DRIVE_USER) using the following scopes:

      | Access | Scope |
      | ------ | ------ |
      | ALL | https://www.googleapis.com/auth/drive |
      | LIST |  https://www.googleapis.com/auth/drive.metadata.readonly |
      | READ | https://www.googleapis.com/auth/drive.readonly |
      | WRITE | https://www.googleapis.com/auth/drive.file |

    Additional Info: [Domain Wide Delegation], [Authorization Scopes]
  
2. Configure Google Drive Storage key:

    **Local Environment**  
    Copy key file (GOOGLE_APPLICATION_CREDENTIALS) specified in *.env* file to expected location (i.e. base project directory)

    **Heroku**
    1. Create config variables
       - GOOGLE_APPLICATION_CREDENTIALS = google-credentials.json  
       - GOOGLE_CREDENTIALS = *\<paste entire service account key json\>*

    2. Add *[google-application-credentials]* buildpack
    3. Push a [tiny change] to re-deploy

3. Update DNS records  
   - if using Gmail, add "anti-spoof" DNS record so mails don't route to SPAM

### Install
1. *Optional:* Take a backup of your database
2. Verify the config files have the correct values: database.ini (*dcp_repo*), .env (*dcp*)
3. Set the "ENV" environment variable and restart your IDE or close your Windows Powershell
4. In your IDE or in a new Windows Powershell, navigate to the *dcp_repo* project root and run the desired build command: 

    **Clean install:** *build.py -t install_full*  
Setup the repository, add initial data, configure Google Drive/Calendar and initialize the web app.  Any existing data is deleted.

    **Upgrade:** *build.py -t upgrade -v \<current_version\>*  
Update the repository and web app with any schema/logic changes.  Existing data is not modified.

    **Other Options:** *build.py -h*  
5. Push the web app code to the target environment
6. Heroku Only: Update config variables if needed (i.e. DEFAULT_SCHOOL_YEAR)

### How-To: Create New Program Year
1. *Optional:* Upgrade app
2. Create new programs in UI (Admin --> Programas)
3. Update DEFAULT_SCHOOL_YEAR (env / config variables)
4. Upload new documents for new year (acuerdo, videos, etc.)

### How-To: Update Calendars
1. Create calendars for new program years (most likely done when creating new program year)
2. Export master "incentive" calendar from previous year
3. Import calendar events to current year's master "incentive" calendar
4. Update dates and export new calendar
5. Import calendar events to individual schools
6. *Optional* If calendar events don't show up in the UI, manually update the CalendarId for the new school / program year (Admin --> Colegio)

** Make sure calendars are set as "public"

### Notes
 - to overwrite remote: *git push -f heroku master*
 - to access heroku bash (cmd line): *heroku run bash -a <app_name>*
 - to cleanup overridden functions:
 
 
 ```sql
  SELECT 'DROP FUNCTION ' || oid::regprocedure
  FROM pg_proc
  WHERE proname = 'sp_dcpupsertreward'  -- name without schema-qualification
  AND pg_function_is_visible(oid);  -- restrict to current search_path
```

### Reference
[Django 3 Install Guide]

[Configure Postgres DSN]: https://stackoverflow.com/questions/7592519/oracle-sql-developer-and-postgresql
[Set result set limit]: https://stackoverflow.com/questions/8842577/how-to-increase-buffer-size-in-oracle-sql-developer-to-view-all-records
[configure SSL]: https://devcenter.heroku.com/articles/acquiring-an-ssl-certificate
[Domain Wide Delegation]: https://support.google.com/a/answer/162106?hl=en
[Authorization Scopes]: https://developers.google.com/drive/api/v2/about-auth
[google-application-credentials]: https://github.com/gerywahyunugraha/heroku-google-application-credentials-buildpack
[tiny change]: https://stackoverflow.com/questions/47446480/how-to-use-google-api-credentials-json-on-heroku
[Django 3 Install Guide]: https://docs.djangoproject.com/en/3.0/intro/install/
[dcprepo]: https://github.com/buffgecko12/dcprepo
[dcp]: https://gitlab.com/buffgecko/dcp
[Change icons]: https://gist.github.com/marlonbernardes/d3d7fd75ee689c2b989b
