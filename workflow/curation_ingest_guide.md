Working Procedures for Curating and Ingesting New Datasets
==========================================================

This guide outlines the procedures for taking in complete datasets that site members wouldn't otherwise want to have to key in through Upload-As-You-Go.

[Initial Request](#initial_request)

[Interpreting Priority and Data Preparedness](#interpret_priority)

[Gather and Assess Data](#gather_assess)

[Process and Load Data](#process_data)


## <a name="initial_request">Initial Request</a>

* When a potential dataset provider initiates a request to have their data added to Databrary, Databrary staff and/or PIs will contact provider to get further details about the nature of their dataset. This includes, but is not limited to:
    - Video, audio, or still images are part of dataset
    - Developmental
        + participants are infants, children, or adolescents and/or parents or other family members
        + is design cross-sectional or longitudinal
    - Additional data or metadata beyond available video
    - Topic/content has high interest or potential impact
        + rare sample
        + topic that would benefit other researchers
        + new data type that is important or compelling to support
    - Study has prior or current funding from NIH or NSF
    - Condition of dataset
        + Archival, in process, to be collected
        + Digitized or analog
        + Degree of conversion/reformatting required
    - Permission/privacy issues
    - Characteristics of data provider
        + Available to help with curation or not
* Document responses to above.

## <a name="interpret_priority">Interpreting Priority and Data Preparedness</a>
Based on the above criteria, priority and preparedness will be used to determine the approximate estimate for when a dataset will be fully ingested and available in Databrary. Incomplete datasets or datasets organized using non-standard or unfamiliar standards will require more time to ingest or might not be ready at the moment for ingestion. Though depending on other criteria, these datasets might take higher priority over those that might be more ready for ingestion from a technical standpoint.

While we will do our best to set out a formal process for determining the priority a dataset takes for the curation and ingestion process, in many situations estimations for inclusion databrary will have to happen on a case by case basis.

## <a name="gather_assess">Gather and Assess Data</a>

* Have data provider upload data to shared server
* Review and explore data, assess further for ingest readiness
* Additional criteria for estimating priority and time to full ingestion will be based on the following (in addition to information gathered from [initial request](#initial_request)):

    - Does dataset consist entirely or mostly of file formats and metadata we already support or can easily support --or-- will system require additional features to accomodate data and metadata?
    - Are data release levels already determined and cleared by institutions grantors and/or IRB --or-- will additional IRB engagement and release level auditing need to take place by the dataset provider?
    - How much Databrary staff time will be required to package data for ingestion?
    -

* Follow up with data provider, where possible and appropriate, to request additional information and provide an approximate idea of when their data will be included in Databrary referencing assessment criteria above.

*

## <a name="process_data">Processing and Load Data</a>

Once a dataset has been approved for starting the ingestion process, Databrary staff will:

* Review video materials for content that will require creation of additional metadata as well as sensitive information not to be released
* Determine and enter data into spreadsheet based on video file and time ranges that comprise a "session"
* Enter and/or shape participant metadata into the establish spreadsheet template (*TBD*)
* Ensure that participant metadata is assigned accurately with session metadata
* Flag any metadata that might need special attention for the ingest process (i.e. needs additional processing or could benefit from automated transformation)
* Arrange assets (videos and other materials) on the server in as per asset directory template (*PENDING*)
* Ensure that files are named according to file naming conventions (*PENDING*)

Once a dataset has been prepared:

* Transform spreadsheet metadata into ingestable JSON format via script and validate against [JSON schema](http://github.com/databrary/curation/spec/volume.json).
* Ingest and transcode metadata and asset data via server scripts.
* Staff will then review materials as they appear on the site and correct any errors that occurred during the ingest process.
*Ensure that data has correct permissions applied to them.

Once the dataset is properly ingested and on the site, Databrary will notify the data provider to review their materials and provide any feedback.
