import math
import time

from rest_framework.views import APIView
from rest_framework.response import Response
import json

from ..Helperclasses.ai import DummyAI
from ..models import *
from ..Helperclasses.jwttoken import JwToken

MAX_POINTS = 100
SECS_PER_YEAR = 31556952
SECS_PER_DAY = 86400

def user_needs_ex(username, id):
    #TODO user needs exercise
    return True

def get_correct_description(username, description):
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
    elif Trainer.objects.filter(username=username).exists():
        user = Trainer.objects.get(username=username)
    elif Admin.objects.filter(username=username).exists():
        user = Admin.objects.get(username=username)
    else:
        return "invalid user"
    lang = user.language
    desc = json.loads(description.replace("'", "\""))
    res = desc.get(lang)
    if res == None:
        return "description not available in "+lang
    return res

def get_lastday_of_month(m, y):
    if m == 1 or m == 3 or m == 5 or m == 7 or m == 8 or m == 10 or m == 12:
        return 31
    elif m == 4 or m == 6 or m == 9 or m == 11:
        return 30
    elif m == 2:
        if y % 400 == 0:
            return 29
        elif y % 100 == 0:
            return 28
        elif y % 4 == 0:
            return 29
        else:
            return 28
    else:
        return -1

class GetExerciseView(APIView):
    def post(self, request, *args, **kwargs):
        req_data = dict(request.data)
        token = JwToken.check_session_token(request.headers['Session-Token'])
        info = token['info']
        #check if token is valid
        if not token["valid"]:
            data = {
                'success': False,
                'description': 'Token is not valid',
                'data': {}
                }
            return Response(data)
        
        #check if requested exercise exists
        if not Exercise.objects.filter(id=int(req_data['id'])).exists():
            data = {
                'success': False,
                'description': 'no exercise with this id exists',
                'data': {}
            }

            return Response(data)

        #check if user is allowed to request
        if not (token["info"]["account_type"] == "trainer" or (token["info"]["account_type"] == "user" and user_needs_ex(token["info"]['username'], int(req_data['id'])))):
            data = {
                'success': False,
                'description': 'Not allowed to request list of exercises',
                'data': {}
                }
            return Response(data)

        #get exercise
        ex = Exercise.objects.get(id=int(req_data['id']))

        #checks wether exercise is activated
        if not ex.activated:
            data = {
                'success': True,
                'description': 'Be careful, exercise is deactivated! Returned data',
                'data': {
                    'title': ex.title,
                    'description': get_correct_description(info['username'], ex.description),
                    'video': ex.video,
                    'activated': False
                }
            }

            return Response(data)
            
        data = {
                'success': True,
                'description': 'Returned data',
                'data': {
                    'title': ex.title,
                    'description': get_correct_description(info['username'], ex.description),
                    'video': ex.video,
                    'activated': True
                }
        }

        return Response(data)


class GetExerciseListView(APIView):
    def get(self, request, *args, **kwargs):
        token = JwToken.check_session_token(request.headers['Session-Token'])
        #check if token is valid
        if not token["valid"]:
            data = {
                'success': False,
                'description': 'Token is not valid',
                'data': {}
                }
            return Response(data)

        info = token['info']
        #only trainers can request all exercises
        if not info['account_type'] == 'trainer':
            data = {
                'success': False,
                'description': 'you are not allow to request all exercises',
                'data': {}
                }
            return Response(data)

        #get all exercises as list
        exercises = Exercise.objects.all()
        exs_res = []
        #get all ids as list
        for ex in exercises:
            exs_res.append({
                'id': ex.id,
                'title': ex.title
                })
        data = {
                'success': True,
                'description': 'returning all exercises',
                'data': {
                    'exercises': exs_res
                }
        }

        return Response(data)

class DoneExerciseView(APIView):
    def post(self, request, *args, **kwargs):
        req_data = dict(request.data)
        token = JwToken.check_session_token(request.headers['Session-Token'])
        if not token["valid"]:
            data = {
                'success': False,
                'description': 'Token is not valid',
                'data': {}
            }
            return Response(data)

        info = token['info']
        user = User.objects.get(username=info['username'])
        eip = ExerciseInPlan.objects.get(id=req_data['exercise_plan_id'])

        if eip == None:
            data = {
                'success': False,
                'description': 'Exercise in plan id does not exists',
                'data': {}
            }
            return Response(data)

        # check if its alrady done this week
        done = DoneExercises.objects.filter(exercise=eip, user=user)
        for d in done:
            # calculate the timespan and if its already done done
            if time.time() - (d.date - d.date%86400) < 604800:
                data = {
                    'success': False,
                    'description': 'User already did this exercise in this week',
                    'data': {}
                }
                return Response(data)

        # calculating points
        a, b, c = DummyAI.dummy_function(ex=eip.exercise.id, video=None)
        intensity = b['intensity']
        speed = b['speed']
        cleanliness = b['cleanliness']

        points = int(math.ceil((intensity + speed + cleanliness) / 3))
        leaderboard_entry = Leaderboard.objects.get(user=user)
        leaderboard_entry.score += points
        leaderboard_entry.save(force_update=True)
        # creating the new DoneExercise entry
        new_entry = DoneExercises(exercise=eip, user=user, points=points, date=int(time.time()))
        new_entry.save()
        data = {
            'success': True,
            'description': 'Done Exercise is now saved',
            'data': {}
        }

        return Response(data)

class GetDoneExercisesView(APIView):
    def GetDone(self, user):
        # list of all done in last week
        # calculation of timespan and filter
        done = DoneExercises.objects.filter(user=user, date__gt=time.time() + 86400 - time.time() % 86400 - 604800)

        # list of all exercises to done
        all = ExerciseInPlan.objects.filter(plan=user.plan)
        out = []
        for a in all:
            done_found = False
            for d in done:
                if a.id == d.exercise.id:
                    out.append({"exercise_plan_id": a.id,
                                "id": a.exercise.id,
                                "date": a.date,
                                "sets": a.sets,
                                "repeats_per_set": a.repeats_per_set,
                                "done": True
                                })
                    done_found  = True
                    break
            if done_found:
                continue

            out.append({"exercise_plan_id": a.id,
                        "id": a.exercise.id,
                        "date": a.date,
                        "sets": a.sets,
                        "repeats_per_set": a.repeats_per_set,
                        "done": False
                        })

        data = {
            "success": True,
            "description": "Returned list of Exercises and if its done",
            "data":
                {"name": user.plan.name,
                 "exercises": out
                 }
        }

        #returns the data as in the get plan but with a additional var "done"
        return data


    def get(self, request, *args, **kwargs):
        #check session token
        token = JwToken.check_session_token(request.headers['Session-Token'])
        if not token["valid"]:
            data = {
                'success': False,
                'description': 'Token is not valid',
                'data': {}
            }
            return Response(data)

        info = token['info']
        user = User.objects.get(username=info['username'])

        #create data in form of get plan
        data = self.GetDone(user)
        return Response(data)

    def post(self, request, *args, **kwargs):
        req_data = dict(request.data)
        #check session token
        token = JwToken.check_session_token(request.headers['Session-Token'])
        if not token["valid"]:
            data = {
                'success': False,
                'description': 'Token is not valid',
                'data': {}
            }
            return Response(data)

        # security: only trainer and admin can access other users data
        if not (token["info"]["account_type"] in ["trainer", "admin"]):
            data = {
                'success': False,
                'description': 'type of account is not allowed to access other users data',
                'data': {}
            }
            return Response(data)

        user = User.objects.get(username=req_data['user'])
        data = self.GetDone(user)
        return Response(data)


class GetDoneExercisesOfMonthView(APIView):

    def get_done_exercises_of_month(self, month, year, user):
        year_offset = (year-1970)*SECS_PER_YEAR
        month_offset = 0
        for i in range(month-1):
            month_offset += get_lastday_of_month(i, year)*SECS_PER_DAY
        next_month_offset = month_offset + get_lastday_of_month(month, year) * SECS_PER_DAY
        offset_gt = year_offset + month_offset - 3600
        offset_lt = year_offset + next_month_offset - 3600
        done = DoneExercises.objects.filter(user=user, date__gt=offset_gt, date__lt=offset_lt)
        # list of all exercises to done
        all = ExerciseInPlan.objects.filter(plan=user.plan)
        out = []
        for d in done:
            out.append({
                "exercise_plan_id": d.exercise.id,
                "id": d.exercise.exercise.id,
                "date": d.date,
                "points": d.points
            })
        return out

    def post(self, request, *args, **kwargs):
        req_data = dict(request.data)
        #check session token
        token = JwToken.check_session_token(request.headers['Session-Token'])
        if not token["valid"]:
            data = {
                'success': False,
                'description': 'Token is not valid',
                'data': {}
            }
            return Response(data)
        info = token['info']
        if info['account_type'] == 'user':
            user = User.objects.get(username=info['username'])
        else:
            data = {
                'success': False,
                'description': 'Not a user',
                'data': {}
            }
            return Response(data)
        done = self.get_done_exercises_of_month(self, month=int(req_data['month']), year=int(req_data['year']), user=user)
        data = {
            'success': True,
            'description': 'Returning exercises done in this month',
            'data': {
                'done': done
            }
        }
        return Response(data)