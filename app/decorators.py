from flask import request, render_template
from functools import wraps


def templated(template=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            template_name = template
            if template_name is None:
                template_name = request.endpoint \
                                    .replace('.', '/') + '.html'

            ctx = f(*args, **kwargs) or {}

            if isinstance(ctx, dict):
                return render_template(template_name, **ctx)
            elif isinstance(ctx, tuple) and isinstance(ctx[0], dict):
                return (render_template(template_name, **ctx[0]),) + ctx[1:]  # not sure if it's readable
            else:
                return ctx

        return decorated_function

    return decorator
