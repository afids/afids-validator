import argparse
from pathlib import Path, PurePath

from fabric import Connection, config


def push_release(
    connection: Connection,
    new_release_path: Path,
    remote_releases_dir: PurePath,
    wheel_name: str,
):
    remote_release_new = str(remote_releases_dir / new_release_path.name)
    connection.run(f"mkdir -p {remote_release_new}")
    wheel_path = str(new_release_path / wheel_name)
    connection.put(wheel_path, remote_release_new)
    connection.put(str(new_release_path / ".env"), remote_release_new)
    link_name = str(remote_releases_dir.parent / "current")
    connection.run(f"ln -s {remote_release_new} {link_name}")


def install_wheel(connection: Connection, venv_path: str, wheel_path: str):
    connection.run(
        f"source {venv_path}/bin/activate && pip install {wheel_path}"
    )


def upgrade_db(
    connection: Connection, new_release_remote: str, venv_path: str
):
    connection.run(
        f"set -a && . {new_release_remote}/.env && set +a && "
        f"{venv_path}/bin/flask -A afidsvalidator.wsgi:app db upgrade "
        f"-d {venv_path}/lib/python3.8/site-packages/migrations"
    )


def restart_validator(connection: Connection):
    connection.sudo("systemctl restart afidsvalidator.service")


def deploy(
    connection: Connection,
    new_release_path: Path,
    remote_releases_dir: PurePath,
    wheel_name: str,
    venv_path: PurePath,
):
    push_release(connection, new_release_path, remote_releases_dir, wheel_name)
    wheel_path = str(remote_releases_dir / new_release_path.name / wheel_name)
    install_wheel(connection, str(venv_path), wheel_path)
    upgrade_db(
        connection,
        str(remote_releases_dir / new_release_path.name),
        str(venv_path),
    )
    restart_validator(connection)


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("host")
    parser.add_argument("new_release_path", type=Path)
    parser.add_argument("remote_releases_dir", type=PurePath)
    parser.add_argument("wheel_name", type=str)
    parser.add_argument("venv_path", type=PurePath)
    parser.add_argument("identity_path", type=Path)
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    deploy(
        Connection(
            args.host, connect_kwargs={"key_filename": str(args.identity_path)}
        ),
        args.new_release_path,
        args.remote_releases_dir,
        args.wheel_name,
        args.venv_path,
    )


if __name__ == "__main__":
    config.Config()
    main()
