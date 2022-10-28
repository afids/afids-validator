import sys

import fabric


def push_release(connection, release_path):
    connection.put(release_path)


def install_wheel(connection, release_str):
    connection.run("source venv/bin/activate && pip install {release_str}")


def upgrade_db(connection):
    connection.run(
        "venv/bin/flask -A afidsvalidator.wsgi:app db upgrade "
        "-d venv/lib/python3.8/site_packages/migrations"
    )


def restart_validator(connection):
    connection.sudo("systemctl restart afidsvalidator.service")


def deploy(connection, release_str, release_path):
    push_release(connection, release_path)
    install_wheel(connection, release_str)
    upgrade_db(connection)
    restart_validator(connection)


if __name__ == "__main__":
    deploy(fabric.Connection(sys.argv[1]), sys.argv[2], sys.argv[3])
