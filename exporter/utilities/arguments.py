#!/usr/bin/env python3

import sys
import configargparse


def get_args():

    parser = configargparse.ArgParser()
    parser.add("--use_v1_uptime_endpoints",
               dest="use_v1_uptime_endpoints",
               env_var="USE_V1_UPTIME_ENDPOINTS",
               default="false",
               type=str.lower,
               choices={'false', 'f', '0', 'off', 'no', 'n', 'off',
                        'true', 't', '1', 'on', 'yes', 'y', 't', 'true', 'on'},
               help='Boolean format string for using the uptime endpoints of the v1 API')

    parser.add("--use_v1_maintenance_windows_endpoints",
               dest="use_v1_maintenance_windows_endpoints",
               env_var="USE_V1_MAINTENANCE_WINDOWS_ENDPOINTS",
               default="false",
               type=str.lower,
               choices={'false', 'f', '0', 'off', 'no', 'n', 'off',
                        'true', 't', '1', 'on', 'yes', 'y', 't', 'true', 'on'},
               help='Boolean format string for using the maintenance windows endpoints of the v1 API')

    parser.add("--username",
               dest="username",
               env_var="USERNAME",
               help='Username for the account')

    parser.add("--api-key",
               dest="api_key",
               env_var="API_KEY",
               help="API key for the account")

    parser.add("--tests.tags",
               dest="tags",
               env_var="TAGS",
               help="A comma separated list of tags used to filter tests "
               "returned from the api")

    parser.add("--logging.level",
               dest="log_level",
               env_var="LOG_LEVEL",
               default="info",
               choices={'debug', 'info', 'warn', 'error'},
               help="Set a log level for the application")

    parser.add("--port",
               dest="port",
               env_var="PORT",
               default=8000,
               help="The TCP port to start the web server on")

    args = parser.parse_args()

    if args.username is None:
        print("Required argument --username is missing")
        print(parser.print_help())
        sys.exit(1)

    if args.api_key is None:
        print("Required argument --api_key is missing")
        print(parser.print_help())
        sys.exit(1)

    return args
