import json
import time

import pandas as pd
from account.caches import cached_auth_group_list, cached_auth_group
from django.db import connection
from django.http import HttpResponse


class RequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.IS_DASHBOARD = False
        if request.path.find('/api/dashboard/') == 0:
            request.IS_API = True
            request.IS_DASHBOARD = True
        elif request.path.find('/api/') == 0:
            request.IS_API = True
        else:
            request.IS_API = False

        response = self.get_response(request)
        return response


class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if path.find('/api/dashboard') == 0 and 'om' not in path and 'login' not in path:
            account = request.user
            if not account.id:
                account = None
            method = request.method
            try:
                payload = str(json.loads(request.body.decode('utf-8')))
            except:
                payload = {}

            response = self.get_response(request)
            status_code = response.status_code
        else:
            response = self.get_response(request)
        return response


class QueryLogger:

    def __init__(self):
        self.queries = []

    def __call__(self, execute, sql, params, many, context):
        current_query = {'sql': sql, 'params': params, 'many': many}
        start = time.monotonic()
        try:
            result = execute(sql, params, many, context)
        except Exception as e:
            current_query['status'] = 'error'
            current_query['exception'] = e
            raise
        else:
            current_query['status'] = 'ok'
            return result
        finally:
            duration = time.monotonic() - start
            current_query['duration'] = duration
            self.queries.append(current_query)


class LoggingQueryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ql = QueryLogger()
        with connection.execute_wrapper(ql):
            # Now we can print the log.

            path = request.path

            account = request.user

            response = self.get_response(request)
        # print('>>>queries', )
        sql = str([x['sql'] for x in ql.queries])
        count = len(ql.queries)
        df = pd.DataFrame([{'api': request.path, 'count': count, 'sql': sql}])
        df.to_csv('/backups/log-api.csv', mode='a', header=False)
        return response
