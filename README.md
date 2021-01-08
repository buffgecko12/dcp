<h1>Duitama Colegio Project - Web App Notes</h1>
These are notes I kept when I configured my development environment.  You can modify them as you see fit.

<h2>Configure Development Environment</h2>
Install and configure the following applications, in order:  

1. JRE SE
2. Eclipse (JavaScript developer) or preferred IDE
  - PyDev
3. PostgreSQL Database
4. Python (32-bit win)
  - pip (may already be included in python install)
  - virtualenv and virtualenvwrapper
  - psycopg2 (Postgres)
  - Django
  - Heroku
  - Pylint
    - disable=C0114,C0115,C0116,bare-except,no-else-return
5. GitBash
6. SQL Data Modeler / Developer
  - Configure Postgres DSN: https://stackoverflow.com/questions/7592519/oracle-sql-developer-and-postgresql
7. Heroku CLI

<h2> Configure Repository project (dcp_repo)</h2>

  - install dependencies (ConfigParser)
  - add libraries to project path (configure src folders)
  - configure database.ini
  - environment variables
  - setx ENV "development" (development environment); requires Eclipse restart

<h2> Configure Application project (dcp)</h2>

  - update environment variables (.env)
  - install dependencies (requirements.txt)
  - configure source folders (/lib, /test)
  - configure load_initial_data scripts (repository, application)
  - configure SSL: https://devcenter.heroku.com/articles/acquiring-an-ssl-certificate

<h2>Configure Google API</h2>

1. Grant Google Project service account user API access to Google Drive user account (GOOGLE_DRIVE_USER)

  - add "all, list, read, write" scopes:
  
	> **ALL**  https://www.googleapis.com/auth/drive  
	> **LIST** https://www.googleapis.com/auth/drive.metadata.readonly  
	> **READ** https://www.googleapis.com/auth/drive.readonly  
    > **WRITE** https://www.googleapis.com/auth/drive.file  

  - https://support.google.com/a/answer/162106?hl=en
  - https://developers.google.com/drive/api/v2/about-auth
  
2. Configure Google Drive Storage key:

  **Local**  
Copy key file specified in .env file (GOOGLE_APPLICATION_CREDENTIALS) to expected location

  **Heroku**
  1. Create config variables
     - GOOGLE_APPLICATION_CREDENTIALS = google-credentials.json  
     - GOOGLE_CREDENTIALS = *\<paste entire service account key json\>*

  2. Add "google-application-credentials" buildpack
      - https://github.com/gerywahyunugraha/heroku-google-application-credentials-buildpack
      
  3. Push a tiny change to re-deploy

	Link: https://stackoverflow.com/questions/47446480/how-to-use-google-api-credentials-json-on-heroku

3. Update DNS records  

 - if using gmail, add "anti-spoof" DNS record so mails don't route to SPAM

<h2>Install</h2>  

1. Open setup.py in the "dcp" project and configure the initial values.  
2. Run build.py in the "dcp_repo" project to install the application.  

This will create all the objects in the repository and then initialize the data, configure Google Drive/Calendar, etc.  

<h2>Reference</h2>
https://docs.djangoproject.com/en/3.0/intro/install/