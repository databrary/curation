
class General(object):

    '''a general set of headers for all possible datasets'''
    participant_headers = ["participantID", 
                           "birthdate", 
                           "date", 
                           "age_days",
                           "gestational_age", 
                           "gender", 
                           "race", 
                           "ethnicity", 
                           "language", 
                           "disability", 
                           "category", 
                           "consent"]

    session_headers = ["name", 
                       "date", 
                       "participantID", 
                       "top", 
                       "pilot", 
                       "exclusion" , 
                       "classification",
                       "setting",  
                       "country",
                       "state",
                       "language", 
                       "consent",
                       "condition", 
                       "group",
                       "tasks",  
                       "clip_in", 
                       "clip_out", 
                       "position",
                       "transcode_options", 
                       "filepath", 
                       "file_media", #these will change in general
                       "file_transcript" # ditto
                       ]


class Childes(object):
    '''childes specific data'''
    '''TODO: add all abbreviated languages to this'''
    language_map = {"eng": "English"}

    session_headers = ["name", 
                       "date", 
                       "participantID", 
                       "top", 
                       "pilot", 
                       "exclusion" , 
                       "classification",
                       "setting",  
                       "country",
                       "state",
                       "language", 
                       "consent",
                       "condition", 
                       "group",
                       "tasks",  
                       "clip_in", 
                       "clip_out", 
                       "position",
                       "transcode_options", 
                       "filepath", 
                       "file_media", 
                       "file_transcript"
                       ]