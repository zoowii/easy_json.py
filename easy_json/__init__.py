# coding: UTF-8
from __future__ import print_function
import collections
from datetime import datetime
import time
import json

__author__ = 'zoowii'


def default_json_serializer(obj):
    """Default JSON serializer."""

    if isinstance(obj, datetime):
        timestamp = time.mktime(obj.timetuple())
        return timestamp
    return obj


def get_private_properties(obj):
    if isinstance(obj, dict):
        d = obj
    elif hasattr(obj, '__dict__'):
        d = obj.__dict__
    else:
        raise RuntimeError('easy_json not support obj not dict and without __dict__')
    keys = d.keys()
    return filter(lambda x: x[:2] == '__', keys)


class JSON(object):
    default_encoding = 'UTF-8'

    @staticmethod
    def is_json_primitive_value(obj):
        if obj is None:
            return True
        clss = [int, str, bool, datetime]
        for cls in clss:
            if isinstance(obj, cls):
                return True
        return False

    @staticmethod
    def to_json_object(obj, serializer=default_json_serializer, ignore_keys=None):
        """
        serialize object with __dict__ property or dict to plain dict, without nested complex objects
        so the result dict can be json.dumps(...) directly

        Some keys will be ignored:
        * key in ignore_keys if it's not None
        * key in obj.__no_json__ if the property exist (also @property decorator works)
        * key in obj.__no_json_serialize__ if the property exist (also @property decorator works)
        * key starts with __ (which means the property with name key is "private"
        * the property whose value is callable (both function and object with method '__call__', but you can json serialize the callable object first manually)
        """
        if JSON.is_json_primitive_value(obj):
            return serializer(obj)
        if isinstance(obj, dict):
            data = obj
        elif hasattr(obj, '__dict__'):
            data = obj.__dict__
        else:
            raise RuntimeError('easy_json not support obj not dict and without __dict__')
        no_serialize_keys = []
        if ignore_keys is not None:
            no_serialize_keys.extend(ignore_keys)
        no_serialize_keys.extend(get_private_properties(data))
        if hasattr(obj, '__no_json__') and obj.__no_json__ is not None:
            no_serialize_keys.extend(obj.__no_json__)
        if hasattr(obj, '__no_json_serialize__') and obj.__no_json_serialize__ is not None:
            no_serialize_keys.extend(obj.__no_json_serialize__)
        no_serialize_keys = set(no_serialize_keys)
        keys = set(data.keys()) - set(no_serialize_keys)
        res = {}
        for key in keys:
            val = data[key]
            if callable(val):
                continue
            if JSON.json_serializable(val):
                res[key] = JSON.to_json(val, serializer=serializer, ignore_keys=ignore_keys)
            else:
                res[key] = serializer(val)
        return res

    @staticmethod
    def json_serializable(obj):
        if isinstance(obj, dict) or hasattr(obj, '__dict__'):
            return True
        else:
            return False

    @staticmethod
    def to_json_array(data, serializer=default_json_serializer, ignore_keys=None):
        res = []
        for item in data:
            res.append(JSON.to_json(item, serializer=serializer, ignore_keys=ignore_keys))
        return res

    @staticmethod
    def to_json(data, serializer=default_json_serializer, ignore_keys=None):
        if isinstance(data, collections.Iterable):
            return JSON.to_json_array(data, serializer=serializer, ignore_keys=ignore_keys)
        else:
            return JSON.to_json_object(data, serializer=serializer, ignore_keys=ignore_keys)

    @staticmethod
    def from_json_to_object(s, cls, encoding=default_encoding):
        """
        deserialize dict or json-string to object of class `cls`

        requirements:
        * the class `cls` has constructor with no params(that is, __init__(self) or with params like (self, *args, **kwargs))

        constraints:
        * Because we never known the type of property of a class,
          nested deserializing is not supported, and json-deserializer(eg. parse integer timestamp to datetime) is not supported yet
        """
        if isinstance(s, str):
            data = json.loads(s, encoding=encoding)
        else:
            data = s
        obj = cls()
        for key in data.keys():
            setattr(obj, key, data[key])
        return obj


    @staticmethod
    def from_json_to_array(s, cls, encoding=default_encoding):
        if isinstance(s, str):
            data = json.loads(s, encoding=encoding)
        else:
            data = s
        res = []
        for item in data:
            res.append(JSON.from_json(item, cls, encoding=encoding))
        return res

    @staticmethod
    def from_json(s, cls, encoding=default_encoding):
        if isinstance(s, str):
            data = json.loads(s, encoding=encoding)
        else:
            data = s
        if isinstance(data, list):
            return JSON.from_json_to_array(data, cls, encoding=encoding)
        else:
            return JSON.from_json_to_object(data, cls, encoding=encoding)
