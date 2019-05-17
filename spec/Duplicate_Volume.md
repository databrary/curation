Duplicate a Databrary Volume
===================================

**Prerequisites**:
- Connect to NYU network or NYU VPN.
- Have admin access to the production server.
- Install iTerm2 (Not mandatory but comes handy when copying from the terminal)

1. Connect to Bastion:
    ```
    ssh -t <NETID>@devdatabrary2.home.nyu.edu
    ```

1. Connect to Production:
    ``` bash
    ssh -t databrary 'sudo -u root sh -c "tmux attach"'
    ```

1. On root window, connect to the Database:
    ``` bash
    psql -U postgres -d databrary
    ```

2. Copy the following query to your terminal (Replace <VOLUME_ID> with your volume ID):
    ``` sql
    select 
    'mkdir -p /nyu/stage/reda/' || a.volume || '/' || sa.container || E'\n' ||
    'cp /nyu/store/' || substr(cast(sha1 as varchar(80)), 3, 2) 
        || '/' || right(cast(sha1 as varchar(80)), -4) 
    || ' /nyu/stage/reda/' || volume || '/' || container || '/'
        || 
        CASE 
            WHEN (substring(a.name from '\.([^\.]*)$') = '') IS NOT FALSE 
            THEN a.name || '.' || f.extension[1]
            ELSE a.name
        END
    from slot_asset sa 
    inner join asset a on sa.asset = a.id 
    inner join format f on a.format = f.id
    where a.volume = <VOLUME_ID>;
    ```
    Note: The query above should return files with extensions but make sure that all the files have an extension otherwise the ingest will not work.

3. Make sure that there is enough space in ```/nyu/stage```
    ``` bash
    df -h /nyu
    ```

4. Exit ```psql```, you should land on the root account
    ```
    \q
    ```
5. Connect to the databrary service account, only databrary user has privileges under ```/nyu/stage``` folder
    ``` bash
    sudo su - databrary
    ```
 
6. Create a bash script under ```/tmp``` folder with vim, start the first line of the script with ```set -x``` and copy the result of the SQL query.

7. Run the script and wait for the files to be copied to the ```/nyu/stage``` directory. (Files for ingest must be moved into a temporary Databrary folder).

8. Now that we have our videos copied, we will need to create the CSV files for the ingest, if you would like to document yourself on how to collect data from users, please check [spec folder](../spec), if you just need to duplicate your volume. First, export it as CSV (Feature available on Databrary), and paste the content into two files one for sessions and one for participants, follow instructions in [metadata.md](metadata.md) to write your files. To avoid uploading your videos again, add file_{#} and fname_{#} columns. 

    **IMPORTANT**: Put the path to the copied videos via the bash script in file_{#} column (e.g., /nyu/stage/reda/slotID/video_name.mp4).

9. Create a new volume on Databrary, you will need the name of the volume in the next step.

10. Follow instructions [here](../README.md) in order to:
       - Set up your environment. 
       - Generate your JSON files. Note: I like to validte the output against the volume schema using your favorite tool (There is many free validator online), this will help you spot any invalid input (Script imporovement: add validation in csv2json.py)
       - Run the Ingest.


