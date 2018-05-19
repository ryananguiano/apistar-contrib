import os
from apistar import App, Route, http
from apistar_contrib.csrf import EnforceCsrfHook, rotate_token


def show_form():
    return app.render_template(
        'form.html',
        show_csrf=True,
    )


def show_no_csrf_form():
    return app.render_template(
        'form.html',
        show_csrf=False,
    )


def handle_form(request: http.Request):
    # You should rotate CSRF tokens after successful login/logout
    rotate_token(request)
    return app.render_template(
        'form.html',
        show_csrf=True,
        success=True,
    )


routes = [
    Route('/', 'GET', show_form),
    Route('/no_csrf', 'GET', show_no_csrf_form),
    Route('/handle', 'POST', handle_form),
]

BASE_DIR = os.path.dirname(__file__)
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

app = App(
    routes=routes,
    event_hooks=[EnforceCsrfHook],
    template_dir=TEMPLATE_DIR,
)
