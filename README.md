# Duitama Colegio Project - Web App
These instructions will allow you to configure your environment and deploy the web app.
### Configure Development Environment
Install and configure the following applications, in order:  

1. JRE SE
2. Eclipse (JavaScript developer) or preferred IDE with PyDev
3. PostgreSQL Database
4. Python (32-bit win) and the following packages:
    - pip (may already be included in python install)
    - virtualenv and virtualenvwrapper
    - psycopg2 (Postgres)
    - Django
    - Heroku
    - Pylint
      - ignore common warnings:  *disable=C0114,C0115,C0116,bare-except,no-else-return*
5. GitBash
6. SQL Data Modeler / Developer
    - [Configure Postgres DSN]
7. Heroku CLI

### Configure Repository

  - clone the *[dcp_repo]* project
  - install dependencies (ConfigParser)
  - add libraries to project path and configure *src* folders
  - configure */database.ini*
  - configure initial values: */src/load_intiial_data.sql*
  - set environment variables and restart IDE: `setx ENV "development"`

### Configure Application

  - clone the *[dcp]* project
  - update environment variables: */.env*
  - install dependencies (*requirements.txt*)
  - configure source directories (*/lib*, */test*)
  - configure initial values: setup.py
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
    Copy key file specified in *.env* file (GOOGLE_APPLICATION_CREDENTIALS) to expected location

    **Heroku**
    1. Create config variables
       - GOOGLE_APPLICATION_CREDENTIALS = google-credentials.json  
       - GOOGLE_CREDENTIALS = *\<paste entire service account key json\>*

    2. Add *[google-application-credentials]* buildpack
    3. Push a [tiny change] to re-deploy

3. Update DNS records  
   - if using gmail, add "anti-spoof" DNS record so mails don't route to SPAM

### Install
Run *build.py* in the *dcp_repo* project root to install the application.  

This will setup the repository, add the initial data, configure Google Drive/Calendar and setup the web app.  

### Reference
[Django 3 Install Guide]

[Configure Postgres DSN]: https://stackoverflow.com/questions/7592519/oracle-sql-developer-and-postgresql
[configure SSL]: https://devcenter.heroku.com/articles/acquiring-an-ssl-certificate
[Domain Wide Delegation]: https://support.google.com/a/answer/162106?hl=en
[Authorization Scopes]: https://developers.google.com/drive/api/v2/about-auth
[google-application-credentials]: https://github.com/gerywahyunugraha/heroku-google-application-credentials-buildpack
[tiny change]: https://stackoverflow.com/questions/47446480/how-to-use-google-api-credentials-json-on-heroku
[Django 3 Install Guide]: https://docs.djangoproject.com/en/3.0/intro/install/
[dcp_repo]: https://gitlab.com/buffgecko/dcp_repo
[dcp]: https://gitlab.com/buffgecko/dcp