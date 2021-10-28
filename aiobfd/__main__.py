"""aiobfd: Asynchronous BFD Daemon"""

import argparse
import socket
import logging
import logging.handlers
import sys
import aiobfd

_LOG_LEVELS = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]

import logging
import logging.config
import logging.handlers

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


def parse_arguments():
    """Parse the user arguments"""
    parser = argparse.ArgumentParser(
        description="Maintain a BFD session with a remote system"
    )
    family_group = parser.add_mutually_exclusive_group()
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

    parser.add_argument(
        "--remote",
        action="append",
        help="<Required> remote IP address or hostname",
        required=True,
    )
    parser.add_argument(
        "--local", type=str, help="Local IP address or hostname"
    )
    parser.add_argument(
        "--control-port",
        type=int,
        default=4784,
        help="Default control port, use 3784 for singlehop",
    )
    parser.add_argument(
        "-r",
        "--rx-interval",
        default=1000,
        type=int,
        help="Required minimum Rx interval (ms)",
    )
    parser.add_argument(
        "-t",
        "--tx-interval",
        default=1000,
        type=int,
        help="Desired minimum Tx interval (ms)",
    )
    parser.add_argument(
        "-m", "--detect-mult", default=1, type=int, help="Detection multiplier"
    )
    parser.add_argument(
        "-p",
        "--passive",
        action="store_true",
        help="Take a passive role in session initialization",
    )
    return parser.parse_args()


def main():
    """Run aiobfd"""
    args = parse_arguments()
    control = aiobfd.Control(
        args.local,
        args.remote,
        family=args.family,
        passive=args.passive,
        rx_interval=args.rx_interval * 1000,
        tx_interval=args.tx_interval * 1000,
        detect_mult=args.detect_mult,
    )
    control.run()


if __name__ == "__main__":
    main()
