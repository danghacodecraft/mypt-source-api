from app.http.models.sdk_permission import *
from app.http.models.sdk_permission_group import *
from app.http.models.sdk_user_permission import *

from django.db import connection

class SdkPermissionHandler:
    def __init__(self):
        pass

    # API nay se lay ra cac permission cua userId nay
    def getAllPermissionsByUser(self, userId):
        query = "SELECT user_per.permission_code, per_group.permission_group_code FROM " + SdkUserPermission._meta.db_table + " AS user_per INNER JOIN " + SdkPermission._meta.db_table + " AS per ON user_per.permission_id = per.permission_id INNER JOIN " + SdkPermissionGroup._meta.db_table + " AS per_group ON per.permission_group_id = per_group.permission_group_id WHERE user_per.user_id = " + str(userId) + " AND per.is_deleted = 0 AND per_group.is_deleted = 0"
        cursor = connection.cursor()
        cursor.execute(query)
        userPerRows = cursor.fetchall()
        persData = {}
        print(userPerRows)
        for userPerRow in userPerRows:
            perCode = userPerRow[0]
            persData[perCode] = {
                "group_code": userPerRow[1]
            }

        return {
            "persData": persData
        }
