from initialize_app import InitApp

class GetDB:
    def __init__(self):
        # initialize once
        self.db1, self.bucket1 = InitApp()

    # return the database and bucket to be used
    def get_db_bucket(self):
        return self.db1, self.bucket1

# to use in your code: 
# from get_db import GetDB
# db, bucket = GetDB().get_db_bucket