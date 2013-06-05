from argparse import ArgumentParser
import universal_functions as uf
import process_units
import unit_functions

def get_args():
    parser = ArgumentParser(description='run the BIP manager.')

    parser.add_argument('-d', '--districts',
            help="extract districts from voterfile and store in units",
            action='store_true')
    parser.add_argument('-rv', '--remove_voterfile',
            help="remove unzipped voterfile post district processing",
            action='store_true')
    parser.add_argument('-c', '--clean_schema',
            help="clear everything (will reset timestamps)",
            action='store_true')
    parser.add_argument('-p', '--partition',
            help="create partitions. You better do this if you clear the schema",
            action='store_true')
    parser.add_argument('-i', '--clean_imports',
            help="remake the import tables",
            action='store_true')
    parser.add_argument('-b', '--build',
            help="import data, rekey, distinct, unions, timestamps, the whole thing",
            action='store_true')
    parser.add_argument('-x', '--export',
            help="create json dumps",
            action='store_true')
    parser.add_argument('-a', '--all',
            help="do everything",
            action='store_true')
    parser.add_argument('-r', '--all_no_clean',
            help="do everything but remake schema and partition",
            action='store_true')

    return parser.parse_args()

def main():
    args = get_args()

    if args.districts:
        process_units.run_foreach_module(unit_functions.compress_districts,remove_voterfile=args.remove_voterfile)
    if args.clean_schema or args.all:
        uf.clean_schema()
    if args.partition or args.all:
        uf.partition()
    if args.clean_imports or args.all or args.all_no_clean:
        process_units.run_foreach_module(unit_functions.clean_import)
    if args.build or args.all or args.all_no_clean:
        process_units.run_foreach_module(unit_functions.build)
    if args.export or args.all or args.all_no_clean:
        uf.dump_json()

if __name__ == "__main__":
    main()
