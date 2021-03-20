from datetime import datetime, timezone
from dateutil import parser, tz
import pytz 
from flask import request, jsonify
from flask_restful import Resource, abort
from mongo import mongodb
from bson import json_util
from bson.objectid import ObjectId
import json

from scheduleapp.scheduler import scheduler

from_zone = tz.tzutc()
to_zone = tz.tzlocal()

def parse_json(data):
    return json.loads(json_util.dumps(data))


def test_job():
    print(datetime.utcnow().replace(tzinfo=to_zone))
    print("Job has run!")


class Schedules(Resource):

    def get(self):

        schedules = list(mongodb.db.schedules.find())
        # print(json.dumps(records, indent=4, sort_keys=True, default=str))
        for schedule in schedules:
            schedule["id"] = str(schedule.pop("_id"))
            local_time = schedule["time"].replace(tzinfo=from_zone).astimezone(to_zone)
            schedule["time"] = datetime.strftime(local_time, "%d/%m/%Y %H:%M")

        return schedules
    
    def post(self):
        request_body = request.json

        print(request_body)
        schedule_time = parser.isoparse(request_body['time'])

        local_schedule_time = schedule_time.replace(tzinfo=from_zone).astimezone(to_zone)
        schedule = mongodb.db.schedules.insert_one({
            "name": request_body['name'],
            "time": local_schedule_time,
            "recipient_name": request_body['recipient_name'],
            "recipient_email": request_body['recipient_email']
        })
        print(schedule.inserted_id)
        scheduler.add_job(func=test_job, trigger='date', run_date=local_schedule_time)
        return {
            'id': str(schedule.inserted_id),
            "name": request_body['name'],
            "time": datetime.strftime(local_schedule_time, "%d/%m/%Y %H:%M"),
            "recipient_name": request_body['recipient_name'],
            "recipient_email": request_body['recipient_email']
        }
    
    def delete(self):
        request_body = request.json
        schedule_id = request_body["id"]
        mongodb.db.schedules.delete_one({'_id': ObjectId(schedule_id)})
    

# class Schedule(Resource):

#     def delete(self, schedule_id):
#         request_body = request.json
        
#         print(mongodb.db.schedules.find_one(schedule_id))