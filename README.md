easy_json.py
===============

a simple python json serialize/deserialize library which is easy to use.

Works well with Django and other Python code

# Author: [zoowii](http://zoowii.com)

# PyPi page
[https://pypi.python.org/pypi/easy_json](https://pypi.python.org/pypi/easy_json)

# Supported Platforms
* Python 3.x
* Python 2.7

# Install
```
pip install easy_install
```
or download the package the command `python setup.py install`

# Usage:
```
from easy_json import JSON

users = User.objects.all()
json = JSON.to_json(users, ignore_keys=['password', '_state'])
users = JSON.from_json(json, User)
return HttpResponse(json)
```

You can also define the ignored keys in model class

```
from django.contrib.auth.models import User
import json

User.__no_json__ = ['password']
user = User.objects.get(username='zoowii')
data = JSON.to_json(user)
json_str = json.dumps(data)
```

User-defined json serializer is also supported
```
data = JSON.to_json_object(user, serializer = lambda x: "Hi, %s" % str(x))
```

