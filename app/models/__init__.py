"""
This MVP uses the Pydantic models in app/schemas/ as both the API contract
AND the in-memory domain representation -- there is no separate ORM/DB
layer yet (the app is currently stateless: every endpoint takes the data it
needs and returns a result, with no persistence).

This module is kept as a placeholder for when persistence is added (e.g.
SQLAlchemy models for storing resumes, JDs, and interview sessions), to
avoid introducing a parallel "domain model" layer that would just
duplicate the schemas today -- that would be unnecessary complexity for
an MVP with no database.
"""
