#!/bin/bash

source "$(poetry env info --path)/bin/activate"
alembic upgrade head
deactivate