Databrary Curation
==================

Curation and ingest tools, scripts, source

**NO Data goes in this repository**

### setup

Must have programs: Python 2.7

Useful programs: iTerm2 (easier interface than Terminal), Sourcetree (local GitHub clone), Sublime Text (.csv and .json editor)

Need an /output directory in /tools (with /scripts)

Open iTerm window in folder /Users/[username]/Documents/GitHub/curation/tools

Create folder for completed .csv files (e.g., /HD/temp)

### spec

#### api_docs

*Not complete*: This folder contains a work in progress for describing the Databrary API using [Swagger IO](http://swagger.io/). 

#### templates

Contains all current templates for Databrary ingest. All files can be generated automatically with the fields from [fields.py](https://raw.githubusercontent.com/databrary/curation/master/tools/scripts/utils/fields.py) and required entries from [volume.json]()

**ingest_template.xlsx**: Excel spreadsheet for distributing to contributors with two worksheets, `sessions` and `participants`. Contributors will input session (including filename and location for the video files they wish to ingest) and participant metadata in a format for ingesting into Databrary.

**participants_template.csv** & **sessions_template.csv**: csv formats for each worksheet in `ingest_template.xlsx`

* Make sure dates are in MM/DD/YYYY format
* Open .csv files in Sublime and convert line endings to Unix
* Make sure text IDs have leading/padding zeros
* Do not include file_position_1 if not using clips
* Release must be in BOTH session and participant .csv
* Make sure filepath does NOT start with "/"

#### volume.json

JSON Schema file which defines constraints, datatypes, accepted values and JSON strutucture for metadata to be ingested into Databrary. Each ingest is validated against this schema before being being written to the Databrary database. Official version is [here](https://raw.githubusercontent.com/databrary/databrary/master/volume.json).

### tools/scripts

**prepareCSV.py**: Script that can be used to download Volume metadatas' in CSV format and build paths to the files located on the server.
The script generates an SQL query that need to be run on the Databrary server prior to the ingest. generated files will be found in the
`input` folder

* Usage: Download and generate sessions and participants files
    ```
    python prepareCSV.py -u YOUR_USERNAME -p PASSWORD -s SOURCE_VOLUME -t TARGET_VOLUME
    ```
  if you have your own curated CSV file (Skip the download phase) and would like to use the script, add the `-f[--file]` argument:
    ```
    python prepareCSV.py -f FILE_PATH -u YOUR_USERNAME -p PASSWORD -s SOURCE_VOLUME -t TARGET_VOLUME
    ```

**csv2json.py**: This is the main ingest script which takes the session and/or participant .CSV files for any given dataset and converts it into a .JSON file (located in the /output folder) which can then be uploaded to `https://nyu.databrary.org/volume/{VOLUME_ID}/ingest` to start the ingest process. Select Run to run the ingest, leave both check boxes blank to check the JSON, Select Overwrite to overwrite existing session data.

* Usage (traditional ingest - pre-assisted curation): 
    ```
    python csv2json.py -s {path to session csv file} -p {path to participant csv file} -f {output JSON name} -n {Full name of volume on Databrary (must match)}
    ```    
    Example: Users-MacBook-Pro:scripts user$ python csv2json.py -s /temp/sessions_template_test.csv -p /temp/participants_template_test.csv -f bergtest -n "ACLEW Project"

* Usage (assisted curation)
    ```
    python csv2json.py -a -s {path to session csv file} -p {path to participant csv file} -f {output JSON name} -n {Full name of volume on Databrary (must match)}
    ```
  
Note: the participant file is optional if you only want to add session metadata. However, you cannot have ParticipantID in the session file if you are ommitting a participant file.

**assisted.py**: Script that can be used to pull rows related to assisted curation uploads from an instance of the Databrary database. Currently does not connect to production.

**make_templates.py**: run in order to generate templates in `$CURATION_HOME/spec/templates`

#### utils 

various scripts for supporting ingest and curation operations 

**./openproject/update.py**: this script will pull all new volumes into our OpenProject tracker.

* Usage: 
    - enter python virtualenvironment: `source ~/curation/tools/scripts/venv2/bin/activate`
    - ssh to www (which should be port forwarded)
    - in `~curation/tools/scripts` run `python -m utils.openproject.update` to see which new volumes will be added and `python -m utils.openproject.update -r` to add those new volumes to OpenProject


**csv_helpers.py**: some helpul functions for routine csv operations in preparing an ingest

**dbclient.py**: db client module for connecting to an instance of a database

**fields.py**: module for all spreadsheet headers for Databrary ingest spreadsheets. Used to generate template spreadsheets

**./videos**: a few scripts for checking video integrity

**./analysis**: mostly one off scripts for various projects integrating with databrary.
