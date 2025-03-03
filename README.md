# Duitama Colegio Project - Web App
These instructions will help you to configure your environment and deploy the web app.  

### Configure Development Environment
**Install and configure the following applications, in order:**  

1. [Eclipse](https://www.eclipse.org/downloads/) ** (or preferred IDE)
    - Install [PyDev](https://www.pydev.org/) add-on ([Install Link](http://www.pydev.org/updates))
    - Install [SQL Editor](https://marketplace.eclipse.org/content/sql-editor/help) add-on ([Install Link](https://de-jcup.github.io/update-site-eclipse-sql-editor/update-site))
    - [Change icons](https://gist.github.com/marlonbernardes/d3d7fd75ee689c2b989b): "C:\home\eclipse\plugins\org.eclipse.epp.package.jee_4.34.0.20241128-0756\" (optional)
2. [PostgreSQL](https://www.postgresql.org/download/)
    - add `bin` directory to system `PATH` variable (i.e. `C:\Program Files\PostgreSQL\17\bin`)
4. [Python](https://www.python.org/downloads/)
5. [Git](https://git-scm.com/downloads)
6. [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli#install-the-heroku-cli)
7. [SQL Data Modeler](https://www.oracle.com/database/sqldeveloper/technologies/sql-data-modeler/download/) (optional) **
8. [SQL Developer](https://www.oracle.com/database/sqldeveloper/technologies/download/) (optional)  **
    - Add [Postgres JDBC driver](https://jdbc.postgresql.org/download/)
    - [Configure Postgres DSN]: Specify hostname: "\<hostname\>/\<database\>?"
    - [Set result set limit]: Specify *ARRAYFETCHSIZE* value in preferences file

  *\*\* requires JRE or [JDK](https://www.oracle.com/java/technologies/downloads/#java23)*



### Configure Repository

  - clone the *[dcprepo]* project
      - if your Git password doesn't work, you may need a [Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
  - update config file: `database.ini`
  - configure initial values: `src/load_intitial_data.sql`
  - configure IDE:
    - specify source directories (i.e. `lib`) as such
    - ~~add library directories to project path~~
    - create new interpreter pointing to correct virtual env (*Scripts/Python.exe*) and set this as the project-specific interpreter

### Configure Web Application

  - clone the *[dcp]* project
  - update environment variables: `.env`
  - configure initial values: `initialdata.py`
  - configure IDE
    - specify source directories (i.e. `lib`, `test`) as such
    - create new interpreter pointing to correct virtual env (*Scripts/Python.exe*) and set this as the project-specific interpreter
  - [configure SSL] (optional depending on environment)

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
    Copy key file (GOOGLE_APPLICATION_CREDENTIALS specified in *.env* file) to expected location (i.e. base project directory)

    **Heroku**
    1. Create config variables
       - GOOGLE_APPLICATION_CREDENTIALS = google-credentials.json  
       - GOOGLE_CREDENTIALS = *\<paste entire service account key json\>*

    2. Add *[google-application-credentials]* buildpack
    3. Push a [tiny change] to re-deploy

3. Update DNS records  
   - if using Gmail, add "anti-spoof" DNS record so mails don't route to SPAM

### Configure environment
1. Create and activate virtual environment via command prompt:
    - `cd \<virtual_envs_dir>` (i.e. c:\home\projects\\.venv\\)
    - `python -m venv <virtual_env_name>`
    - `<virtual_env_name>\Scripts\activate.bat`
    - add a path file with source directories to emulate `%PYTHONPATH%`:
      - `echo import sys;sys.path.append('<lib_path_escaped>'); > <virtual_env_name>\Lib\site-packages\<app_name>dcp.pth`
      - i.e. `echo import sys;sys.path.append('C:\\home\\projects\\dcp\\test\\');sys.path.append('C:\\home\\projects\\dcp\\lib\\'); > c:\home\projects\.venv\dcp2-prd\lib\site-packages\dcp.pth`
     
2. Install dependencies  
    - `pip install -r \<path_to_requirements_file>` (*requirements.txt* file is in main app's base directory)  
    - `pip install configparser` (used by installer to read config files)

### Install
1. Take a backup of your database (optional)
2. Verify config files have the correct values: `database.ini` (*dcprepo*), `.env` (*dcp*)
3. Set the "ENV" environment variable in a command prompt
    - `setx ENV "development"` (valid values: development, test, staging, production)
    -  restart your IDE or close your Windows Powershell
4. In your IDE or in a new Windows Powershell, navigate to the *dcprepo* project root and run the desired build command: 

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

### How-To: Build / Deploy Code
1. Configure a [Heroku remote](https://devcenter.heroku.com/articles/git#create-a-heroku-remote)
2. Push change to Heroku "remote": _git push heroku <source_branch>:master_

### Notes
 - to overwrite remote: *git push -f heroku master*
 - to access heroku bash (cmd line): *heroku run bash -a <app_name>*
 - install PyLint (optional): `pip install Pylint`
      - ignore common warnings:  *disable=C0114,C0115,C0116,bare-except,no-else-return*
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
[dcp]: https://github.com/buffgecko12/dcp
[Change icons]: https://gist.github.com/marlonbernardes/d3d7fd75ee689c2b989b
