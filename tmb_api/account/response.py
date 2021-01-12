import datetime

from rest_framework.response import Response as RestResponse


class Response(RestResponse):

    def __init__(self, data=None, status=None,
                 template_name=None, headers=None,
                 exception=False, content_type=None):
        super().__init__(data=data, status=status,
                         template_name=template_name, headers=headers,
                         exception=exception, content_type=content_type)

        if isinstance(self.data, dict):
            map_dict = {
                'api': 'web',
                'Who create': 'Jade Jaa',
                'Datetime API trigger': (datetime.date.today()).strftime("%d-%b-%Y %H:%M:%S")
            }
            map_dict.update(self.data)
            self.data = map_dict
