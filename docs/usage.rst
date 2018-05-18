=====
Usage
=====

Local Session Store
```````````````````

.. code-block:: python

    from apistar import App, Route, http
    from apistar_contrib.sessions import SessionComponent, Session
    from apistar_contrib.sessions.local import LocalMemorySessionHook


    def index(session: Session, params: http.QueryParams):
        for key, value in params:
            session[key] = value
        return session.data


    def clear_session(session: Session):
        session.clear()
        return session.data


    routes = [
        Route('/', 'GET', index),
        Route('/clear', 'GET', clear_session),
    ]

    app = App(
        routes=routes,
        components=[SessionComponent()],
        event_hooks=[LocalMemorySessionHook]
    )


CSRF Token
``````````

.. code-block:: python

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
        rotate_token(request)  # You should rotate CSRF tokens after successful POSTs
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

    # templates/form.html

.. code-block:: html

    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>CSRF Form</title>
    </head>
    <body>
        <ul>
            <li><a href="{{ reverse_url('show_form') }}">Form with CSRF</a></li>
            <li><a href="{{ reverse_url('show_no_csrf_form') }}">Form without CSRF</a></li>
        </ul>
        {% if success %}<h1>Successful POST</h1>{% endif %}
        <form action="{{ reverse_url('handle_form') }}" method="post">
            {% if show_csrf %} {{ csrf_token() }} {% endif %}
            <button type="submit">Submit form {% if show_csrf %}with{% else %}without{% endif %} CSRF</button>
        </form>
    </body>
    </html>

