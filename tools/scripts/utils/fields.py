
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
                           "consent"]

    session_headers = ["name",
                       "key",
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
                       "position",
                       "transcode_options",
                       "filepath",
                       "file_1",
                       "fname_1",
                       "fposition_1"
                       "clip_out_1",
                       "clip_in_1",
                       "file_2",
                       "fname_2"
                       "fposition_2",
                       "clip_out_2",
                       "clip_in_2"
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
                       "position",
                       "transcode_options",
                       "filepath",
                       "file_transcript",
                       "file_media"
                       ]
