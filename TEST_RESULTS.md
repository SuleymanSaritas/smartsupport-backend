# Unit Test Results
Date: 02.01.2026
Environment: Docker (Linux/Python 3.9)

## Execution Log
artsupport-backend python -m pytest
=========================== test session starts ============================
platform linux -- Python 3.9.25, pytest-7.4.3, pluggy-1.6.0 -- /usr/local/bin/python
cachedir: .pytest_cache
rootdir: /app
configfile: pytest.ini
testpaths: tests
plugins: anyio-3.7.1
collected 6 items                                                          

tests/test_api.py::test_read_root PASSED                             [ 16%]
tests/test_api.py::test_create_ticket PASSED                         [ 33%]
tests/test_api.py::test_create_ticket_missing_api_key PASSED         [ 50%]
tests/test_api.py::test_create_ticket_invalid_api_key PASSED         [ 66%]
tests/test_api.py::test_rate_limit PASSED                            [ 83%]
tests/test_api.py::test_health_check PASSED                          [100%] 

============================= warnings summary =============================
app/core/db.py:40
  /app/app/core/db.py:40: MovedIn20Warning: The ``declarative_base()`` function is now available as sqlalchemy.orm.declarative_base(). (deprecated since: 2.0) (Background on SQLAlchemy 2.0 at: https://sqlalche.me/e/b8d9)        
    Base = declarative_base()

app/main.py:77
  /app/app/main.py:77: DeprecationWarning:
          on_event is deprecated, use lifespan event handlers instead.      

          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).

    @app.on_event("startup")

../usr/local/lib/python3.9/site-packages/fastapi/applications.py:4547
  /usr/local/lib/python3.9/site-packages/fastapi/applications.py:4547: DeprecationWarning:
          on_event is deprecated, use lifespan event handlers instead.      

          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).

    return self.router.on_event(event_type)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html     
====================== 6 passed, 3 warnings in 7.86s =======================
## Summary
- **Total Tests:** 6
- **Passed:** 6
- **Failed:** 0
- **Modules Verified:** API Endpoints, Rate Limiting, Database Connection, Celery Task Creation.