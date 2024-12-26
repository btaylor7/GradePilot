class Config:
    SECRET_KEY = 'abc123' #Standard with Flask apps, required to run!

    OPENAI_API_KEY = '**********' #Obtained from OpenAI.
    
    UPLOAD_FOLDER = r'path/to/upload/folder/in/static'

    DB_HOST = 'localhost'
    DB_PORT = '5432'
    DB_NAME = '**********'
    DB_USER = '**********'
    DB_PASSWORD = '**********'

#All credentials, keys and upload folder will be specific to the device the system is run on. Fill as appropriate.
#Config is a separate file to make any changes to configurations simpler and easier to carry out without needing to change other files.