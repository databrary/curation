available_fields = ["setting", "country", "state", "language", "info", "category"]

participant_headers = ["participantID", "birthdate", "date", "age_days", "gender", "race", "ethnicity", "language", "disability", 
"category", "consent"]
session_headers = ["name", "date", "participantID", "top", "pilot", "exclusion" , "classification", "clip_in", "clip_out", "position", "filepath", "file_media", "file_transcript", "condition", "group", "language", "setting", "state", "country", "consent"]


record_map = {}
category_map = {}


class Childes(object):

    '''TODO: add all abbreviated languages to this'''
    language_map = {"eng": "English"}