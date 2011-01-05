from paste.script import templates
from paste.script.templates import var

def _random_string(length=12):
    import random
    import string
    result = ''
    for i in range(length):
        result += random.choice(string.letters + string.digits)
    return result

class OpenblockTemplate(templates.Template):
    required_templates = []
    use_cheetah = False
    summary = "Basic OpenBlock project template"
    _template_dir = 'project_templates/openblock'
    
    vars = [
        var('password_salt',
            'Salt used to hash passwords',
            default=_random_string()),
        var('reset_salt',
            'Salt used to hash password resets', 
            default=_random_string()),
        var('staff_cookie_val',
            'Secret cookie value used to identify staff', 
            default=_random_string())
    ]