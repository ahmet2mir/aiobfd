"""aiobfd: Asynchronous BFD Daemon"""
# standard
import sys
import socket
import argparse
import os, os.path
import logging, logging.config, logging.handlers

# local
import aiobfd

logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                "()": "logging.Formatter",
                "format": "[%(asctime)s] [%(process)d] [%(levelname)s] [%(name)s.%(module)s.%(funcName)s:%(lineno)d] %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S %z",
            }
        },
        "handlers": {
            "console": {
                "level": os.environ.get("AIOBFD_LOGLEVEL", "INFO").upper(),
                "class": "logging.StreamHandler",
                "formatter": "simple",
            }
        },
        "loggers": {
            "aiobfd": {
                "level": os.environ.get("AIOBFD_LOGLEVEL", "INFO").upper(),
                "handlers": ["console"],
            },
        },
    }
)


def get_parser():
    """Parse t
    he user arguments"""
    parser = argparse.ArgumentParser(
        description="Maintain a BFD session with a remote system"
    )

    subparser = parser.add_subparsers(dest="command")
    run = subparser.add_parser("run")
    check = subparser.add_parser("check")

    for prs in [run, check]:
        family_group = prs.add_mutually_exclusive_group()
        family_group.add_argument(
            "-4",
            "--ipv4",
            action="store_const",
            dest="family",
            default=socket.AF_UNSPEC,
            const=socket.AF_INET,
            help="Force IPv4 connectivity",
        )
        family_group.add_argument(
            "-6",
            "--ipv6",
            action="store_const",
            dest="family",
            default=socket.AF_UNSPEC,
            const=socket.AF_INET6,
            help="Force IPv6 connectivity",
        )

        prs.add_argument(
            "--remote",
            action="append",
            help="<Required> remote IP address or hostname",
            required=True,
        )
        prs.add_argument(
            "--local", type=str, help="Local IP address or hostname"
        )
        prs.add_argument(
            "--control-port",
            type=int,
            default=4784,
            help="Default control port, use 3784 for singlehop",
        )
        prs.add_argument(
            "-r",
            "--rx-interval",
            default=1000,
            type=int,
            help="Required minimum Rx interval (ms)",
        )
        prs.add_argument(
            "-t",
            "--tx-interval",
            default=1000,
            type=int,
            help="Desired minimum Tx interval (ms)",
        )
        prs.add_argument(
            "-m",
            "--detect-mult",
            default=1,
            type=int,
            help="Detection multiplier",
        )
        prs.add_argument(
            "-p",
            "--passive",
            action="store_true",
            help="Take a passive role in session initialization",
        )
        prs.add_argument(
            "--state-dir",
            default="/run/aiobfd",
            help="Directory where to persist state on filesystem.",
        )

    return parser


def main():
    """Run aiobfd"""
    parser = get_parser()

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    if not args.state_dir is None and not os.path.exists(args.state_dir):
        raise RuntimeError(
            f"Path {args.state_dir} doesn't exists or not accessible please ensure that it exists and writable by current user"
        )

    if args.command == "run":
        control = aiobfd.Control(
            local=args.local,
            remotes=args.remote,
            family=args.family,
            passive=args.passive,
            rx_interval=args.rx_interval * 1000,
            tx_interval=args.tx_interval * 1000,
            detect_mult=args.detect_mult,
            state_dir=args.state_dir,
        )
        control.run()
    elif args.command == "check":
        if not aiobfd.Control.check(
            local=args.local, remotes=args.remote, state_dir=args.state_dir
        ):
            sys.exit(1)


if __name__ == "__main__":
    main()
