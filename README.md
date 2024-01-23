# DIGITHAI Code Challenge (Python)

Hello! this is my code challenge submission.

## Run using Docker

```bash
# Build
docker build -t digithai-challenge-jz .

# Run
docker run -d -p 8000:8000 --name digithai_challenge_jz --rm digithai-challenge-jz

# Stop
docker stop digithai_challenge_jz
```

## Run using venv

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd notes_project
python manage.py runserver
```

## Test
```bash
pytest
python manage.py test
```

## User Credentials

Two test users have been set up

### Superuser

* username: root
* password: root

### Normal user

* username: jerry
* password: abcd1234*

## Notes

* Alternatively can run on a VSCode devcontainer. I've included my own VSCode devcontainer and launch configurations. After starting the devcontainer the window may need to be reloaded for the VSCode extensions to install correctly.
* Pre-commit is set up to run linting and formatting hooks inside the devcontainer.
* I've used factory_boy for tests because it's what I'm most familiar with at the moment.

### Nice to have and other thoughts

Some things which would be nice to have but I haven't added include:

* The ability to sort by the title, created and modified fields on the main notes list page.
* Custom error page templates for 500, 404, 403, etc.
* Including the note title slug in the URL, and using a hashed value for the identifier instead of the pk directly.
* Pagination.

Thank you for reviewing.
