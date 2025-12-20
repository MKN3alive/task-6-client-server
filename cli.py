import requests
import argparse

BASE_URL = "http://127.0.0.1:8000"


def create(args):
    params = {}
    for p in args.param:
        if "=" not in p:
            raise ValueError("Parameter must be in form key=value")
        k, v = p.split("=", 1)
        params[k] = float(v)

    data = {
        "name": args.name,
        "expression": args.expr,
        "params": params
    }

    r = requests.post(f"{BASE_URL}/functions", json=data)
    print(r.json())


def list_funcs(_):
    r = requests.get(f"{BASE_URL}/functions")
    print(r.json())


def compute(args):
    if args.name:
        url = f"{BASE_URL}/functions/by-name/{args.name}/compute"
    elif args.id:
        url = f"{BASE_URL}/functions/{args.id}/compute"
    else:
        raise ValueError("Specify --name or --id")

    r = requests.post(url, json={"x": args.x})
    print(r.json())


def delete(args):
    if args.name:
        url = f"{BASE_URL}/functions/by-name/{args.name}"
    elif args.id:
        url = f"{BASE_URL}/functions/{args.id}"
    else:
        raise ValueError("Specify --name or --id")

    r = requests.delete(url)
    print(r.json())

def update(args):
    data = {}

    if args.name_new:
        data["name"] = args.name_new
    if args.expr:
        data["expression"] = args.expr
    if args.param:
        params = {}
        for p in args.param:
            if "=" not in p:
                raise ValueError("Parameter must be in form key=value")
            k, v = p.split("=", 1)
            params[k] = float(v)
        data["params"] = params

    if not data:
        raise ValueError("Nothing to update")

    if args.name:
        url = f"{BASE_URL}/functions/by-name/{args.name}"
    elif args.id:
        url = f"{BASE_URL}/functions/{args.id}"
    else:
        raise ValueError("Specify --name or --id")

    r = requests.put(url, json=data)
    print(r.json())


parser = argparse.ArgumentParser(description="CLI client for function server")
sub = parser.add_subparsers(dest="command", required=True)

# ---- create ----
p_create = sub.add_parser("create", help="Create function")
p_create.add_argument("--name", required=True)
p_create.add_argument("--expr", required=True)
p_create.add_argument(
    "--param",
    action="append",
    default=[],
    help="key=value (can be repeated)"
)
p_create.set_defaults(func=create)

# ---- list ----
p_list = sub.add_parser("list", help="List functions")
p_list.set_defaults(func=list_funcs)

# ---- compute ----
p_compute = sub.add_parser("compute", help="Compute function")
p_compute.add_argument("--x", type=float, required=True)
p_compute.add_argument("--id")
p_compute.add_argument("--name")
p_compute.set_defaults(func=compute)

# ---- update ----
p_update = sub.add_parser("update", help="Update function")
p_update.add_argument("--id")
p_update.add_argument("--name", help="Existing function name")
p_update.add_argument("--name-new", help="New function name")
p_update.add_argument("--expr", help="New expression")
p_update.add_argument(
    "--param",
    action="append",
    default=[],
    help="key=value (can be repeated, replaces params)"
)
p_update.set_defaults(func=update)


# ---- delete ----
p_delete = sub.add_parser("delete", help="Delete function")
p_delete.add_argument("--id")
p_delete.add_argument("--name")
p_delete.set_defaults(func=delete)

args = parser.parse_args()
args.func(args)
