# server defines
VERSION = '1.0'
NAME    = 'T-800 Model 101'

# local defines
FILE_CONFIG    = 'config.yaml'
FILE_MODEL     = 'model.h5'
FILE_WORDS     = 'words.pkl'
FILE_CLASSES   = 'classes.pkl'

# Variables recognition
REGEX          = r"\{\{([A-Za-z0-9,\*%:\+\-\ ]+)\}\}"         # pattern match for {{vars}}
IGNORE_WORDS   = ['?', '!', ',']                            # Ignore these words from learning process
