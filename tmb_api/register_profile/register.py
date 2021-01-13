from rest_framework import status
from account.config_register import data as config_register
"""
    TYPE FILED::
    - 0 information
    - 1 sacle
    - 2 radio
    - 4 text area
    - 5 text
    - 6 number
    - 8 dropdown
    - 10 date picker
    - 12 checkbox
    - 13 dropdown 2 columns
"""


class Register:
    __available_fields = [
        'username',
        'user_id',
        'email',
        'password',
        'title_name',
        'first_name',
        'middle_name',
        'last_name',
        'gender',
        'date_of_birth',
        'address',
        'phone',
        'id_card',
        'licence_id',
        'company_name',
        'year_of_experience',
        'custom_field',
    ]

    __unable_edit_field_list = [
        'username',
        'user_id',
        'email',
        'password',
    ]

    def __init__(self):
        self.__register_fomr_dict = config_register

    def initial_register_profile(self):
        register_form_dict = self.get_register_form
        is_editable = register_form_dict.get('is_editable', True)
        if is_editable:
            initial_register_profile_log = Log.objects.filter(
                group='REGISTER_PROFILE',
                code='INITIAL_REGISTER_PROFILE',
                status='CREATE',
                status_code=status.HTTP_201_CREATED
            ).first()

            if initial_register_profile_log and is_editable:
                is_editable = False
                register_form_dict['is_editable'] = is_editable
                Config.set_value('config-register-form', register_form_dict)
                config_cached_refresh()
            else:
                is_editable = False
                Log.push(None, 'REGISTER_PROFILE', 'INITIAL_REGISTER_PROFILE', None, 'CREATE', status.HTTP_201_CREATED)
                register_form_dict['is_editable'] = is_editable
                Config.set_value('config-register-form', register_form_dict)
                config_cached_refresh()

        return is_editable

    @property
    def is_editable(self):
        register_form_dict = self.get_register_form
        is_editable = register_form_dict.get('is_editable', True)
        if is_editable:
            initial_register_profile_log = Log.objects.filter(
                group='REGISTER_PROFILE',
                code='INITIAL_REGISTER_PROFILE',
                status='CREATE',
                status_code=status.HTTP_201_CREATED
            ).first()

            if initial_register_profile_log:
                is_editable = False
        return is_editable

    @property
    def __get_register_form(self):
        return self.__register_form_dict if self.__register_form_dict else {}

    @property
    def get_available_field_list(self):
        return self.__available_fields

    @property
    def get_register_form(self):
        return self.__get_register_form

    @property
    def get_register_form_client(self):
        from account.config_register import data as config_register
        register_form_dict = config_register

        result_field_list = []
        register_field_list = register_form_dict.get('field_list', [])
        for register_field in register_field_list:
            _result = {}
            key = register_field.get('key', '')
            name = register_field.get('name', '')
            if (name in self.get_available_field_list) or (key[0:12] in self.get_available_field_list):
                if register_field.get('key') is not None:
                    _result['key'] = register_field['key']
                if register_field.get('name') is not None:
                    _result['name'] = register_field['name']
                if register_field.get('placeholder') is not None:
                    _result['placeholder'] = register_field['placeholder']
                if register_field.get('type') is not None:
                    _result['type'] = register_field['type']
                if register_field.get('username_type') is not None:
                    _result['username_type'] = register_field['username_type']
                if register_field.get('is_optional') is not None:
                    _result['is_optional'] = register_field['is_optional']
                if register_field.get('min_length') is not None:
                    _result['min_length'] = register_field['min_length']
                if register_field.get('max_length') is not None:
                    _result['max_length'] = register_field['max_length']

                if register_field.get('choice_list') is not None:
                    choice_list = []
                    for choice in register_field['choice_list']:
                        choice_dict = {}
                        choice_dict['name'] = choice['name']
                        choice_dict['value'] = choice['value']
                        choice_list.append(choice_dict)
                    _result['choice_list'] = choice_list

                result_field_list.append(_result)
                if key == 'password' and register_field.get('is_confirm_password', False):
                    confirm_password = {
                        'key': 'confirm_password',
                        'name': 'confirm_password',
                        'placeholder': 'confirm_password',
                        'type': 5,
                        'is_optional': False
                    }
                    result_field_list.append(confirm_password)

        newsletter = {
            "key": "is_subscribe",
            "name": "subscribe_newsletter",
            "placeholder": "subscribe_newsletter",
            "type": 12,
            "is_optional": True,
        }
        result_field_list.append(newsletter)
        register_form_dict['field_list'] = result_field_list
        return register_form_dict

    def update_register_form(self, data):
        register_field_list = data.get('field_list', [])

        for i, register_field in enumerate(register_field_list):
            field_key = register_field.get('key', '')
            register_field['sort'] = i + 1
            register_field['placeholder'] = register_field['name']

            if field_key in ['username', 'password', 'code', 'email']:
                register_field['is_editable'] = False
                register_field['is_default'] = True

            if field_key == 'username':
                username_type = register_field.get('username_type')
                if username_type == 'username':  # username
                    register_field['username_type'] = 'username'
                elif username_type == 'email':  # email
                    register_field['username_type'] = 'email'
                    register_field['name'] = 'email'
                    register_field['placeholder'] = 'email'

                condition_list = register_field.get('condition_list', [])
                for condition in condition_list:
                    condition_key = condition.get('key')
                    if condition_key == 'lower':
                        is_lower = condition.get('value', False)
                    elif condition_key == 'upper':
                        is_upper = condition.get('value', False)
                    elif condition_key == 'number':
                        is_number = condition.get('value', False)


        # Save config
        register_form_dict = self.get_register_form
        register_form_dict['is_editable'] = self.is_editable
        register_form_dict['field_list'] = register_field_list
