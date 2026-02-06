from invoke import task


@task
def run(c):
    "Run web server on local machine"
    c.run('npx tailwindcss '
          '-c templates/tailwind.config.js '
          '-i templates/tailwind.css '
          '-o static/css/tailwind.css -w', asynchronous=True)
    c.run('uv run --group local flask run', echo=True)


@task
def test(c):
    c.run('uv run --group local pytest', echo=True, warn=False)
    c.run('rm -rf .coverage coverage.json .pytest_cache')


@task
def deploy(c):
    test(c)
    c.run('git push production main', echo=True)


# other
@task
def css(c):
    c.run('npx tailwindcss -c templates/tailwind.config.js -i templates/tailwind.css -o static/css/tailwind.css')
