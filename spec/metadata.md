Databrary Ingest Metadata Schema
================================

Below are the metadata elements for ingesting datasets into Databrary along with descriptions, formatting constraints, required fields, and example input for each field.

### Participant Metadata



| field         | required | multiple | description                                                                                                                   | format            | example                       | notes |
|---------------|----------|----------|-------------------------------------------------------------------------------------------------------------------------------|-------------------|-------------------------------|-------|
| name          | no       | no       | A label or identifier for the session                                                                                         | Text              |                               |       |
| key           | yes      | no       | A unique identifier for this session. This will be important for modifying existing sessions in subsequent ingest operations. | Alphanumeric      | 6002_09                       |       |
| date          | yes      | no       | Date for the session                                                                                                          | Date in ISO-8601  | 2010-09-12                    |       |
| participantID | yes      | no       | Unique identifier for a participant                                                                                           | Alphanumeric      | 6002                          |       |
| top           | no       | no       | Indicator that the container is a top level container (and therefore used for materials and is not a study session).          | "top" or ""       | top                           |       |
| pilot         | no       | no       | Indicator that a session was a study pilot for exploring the study protocol and therefore not included in any analyses.       | "pilot" or ""     | pilot                         |       |
| exclusion     | no       | no       | Reason for session not being included in the study                                                                            | Text              | Procedural/experimenter error |       |
| setting       | no       | no       | Setting in which the study session took place                                                                                 | Text              | Lab                           |       |
| country       | no       | no       | Country in which the study session took place                                                                                 | Text              | US                            |       |
| state         | no       | no       | State in which the study session took place   