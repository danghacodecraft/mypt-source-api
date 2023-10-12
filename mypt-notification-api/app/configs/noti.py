NOTI_HEAD = {
    "to": "",
    "mutable_content": True,
    "content_available": True,
    "priority": "high",
    "notification": {  
    },
}

NOTI_DATA = {
    "data": {
        "content": {
            "id": 1,
            "channelKey": "defaults",
            "title": "",
            "body": "",
            "groupKey":None, # khong co cx dc
            "summary":"",
            "icon":"",
            "largeIcon":"",
            "notificationLayout": "Default", # loai Default, BigPicture, BigText, Inbox, ProgressBar, Messaging, MessagingGroup, MediaPlayer
            "category":None, # loai Alarm, Call, Email, Error, Event, LocalSharing, Message, MissedCall, Navigation, Progress, Promo, Recommendation, Reminder, Service, Social, Status, StopWatch, Transport, Workout
            "bigPicture": "",
            "customSound":"",
            "wakeUpScreen":True,
            "fullScreenIntent":False,
            "criticalAlert": False,
            "roundedLargeIcon": False,
            "roundedBigPicture": False,
            "showWhen": True,
            "autoDismissible": True,            
            "payload": {
                # "actionType":"", # go_to_screen, open_url_in_app, open_url_in_browser, open_app
                # "dataAction":"", # /login, /home, /profile, /test, /check-in, /check-in-history, /info_checkin/map, /notificationDetail, /notification, /onboarding, /permission, /permission/opensetting
                "notifyActionType": "",
                "notifyDataAction": "",
                "popupDetailActionType": "",
                "popupDetailDataAction": "",
                "popupDetailLabel": "",
                "videoUrl":"",
                "noti_identify": {
                    "noti_id": None,
                    "sender_id": None,
                    "send_at": None
                },

                "extraData":None
                # {
                #     # "status": "doing",
                #     # "receiverEmail": "tunh18@fpt.com.vn",
                #     # "messageData": {
                #     #     "idTicket":"32708",
                #     #     "dateComment":"dateComment",
                #     #     "linkUuid": "",
                #     #     "email": "phuongnam.toanpn@fpt.net",
                #     #     "name": "Phạm Như Toàn",
                #     #     "cmt": "Tin nhắn test",
                #     #     "state": 0,
                #     #     "linkImg": [],
                #     #     "avatarImg": "ssdss",
                #     #     "txtDateCmt": "14/07/2021 16:54"
                #     # }
                # }
            }
        },
        "actionButtons":None
        # "actionButtons": [
        #     {
        #         "key": "reply",
        #         "label": "Trả lời",
        #         "autoCancel": true,
        #         "requireInputText": true
        #     },
        #     {
        #         "key": "openChat",
        #         "label": "Xem nội dung",
        #         "autoCancel": true,
        #         "requireInputText": False
        #     }
        # ]
    }
}

NOTI_MUTI_HEAD = {
    "registration_ids": [],
    "mutable_content": True,
    "content_available": True,
    "priority": "high",
    "notification": {  
    },
}
