from tabulate import tabulate
import argparse
import re

from analysis.manager import DBManager

parser = argparse.ArgumentParser(
    prog='SAR Project Analyser',
    description='Tool to analyse the results of the Artery/Omnet++/SUMO simulations'
)
parser.add_argument('-d', '--db', type=str, help='Database path')
parser.add_argument('--db_folder', type=str, help='Databases folder path')

class Node:
    def __init__(self, node_id: int, x_id: int, y_id: int, trans_id: int, recep_id: int) -> None:
        self.node_id= node_id
        self.pos_x_vector_id= x_id
        self.pos_y_vector_id = y_id
        self.transmission_ca_vector_id = trans_id
        self.reception_ca_vector_id= recep_id

def get_all_x_positions_of_node_i(db_path: str, id_node: int):
    
    tables: dict = {
        "from_": {
            "table": "vectorData",
            "as": "vecData",
            "on": "vectorId"
        },
        "inner_join_": [
            {
                "table": "vector",
                "as": "vec",
                "on": "vectorId"
            }
        ]
    }

    fields_to_select: list[dict] = [
        {
            "column": "value",
            "table": "vectorData",
            "as": "X"
        }
    ]

    conditions: list[dict] = [
        {
            "table": "vector",
            "col": "vectorId",
            "value": id_node
        }
    ]

    manager = DBManager(db_path)
    data = manager.select(tables, fields_to_select, conditions)

    return data

def find_substring_between_elements(input_string, start_element, end_element):
    pattern = re.escape(start_element) + r'(.*?)' + re.escape(end_element)
    match = re.search(pattern, input_string)
    return match.group(1) if match else None

def compare_transmission_reception(db_path: str):
    manager = DBManager(db_path=db_path)
    receptions = manager.select(
        tables={
            "from_": {
                "table": "vector"
            }
        },
        fields_to_select=[
            {
                "table": "vector",
                "column": "vectorId"
            },
            {
                "table": "vector",
                "column": "moduleName"
            },
            {
                "table": "vector",
                "column": "vectorCount"
            }
        ],
        conditions=[
            {
                "table": "vector",
                "col": "vectorName",
                "value": "reception:vector(camStationId)"
            }
        ]
    )

    transmissions = manager.select(
        tables={
            "from_": {
                "table": "vector"
            }
        },
        fields_to_select=[
            {
                "table": "vector",
                "column": "vectorId"
            },
            {
                "table": "vector",
                "column": "moduleName"
            },
            {
                "table": "vector",
                "column": "vectorCount"
            }
        ],
        conditions=[
            {
                "table": "vector",
                "col": "vectorName",
                "value": "transmission:vector(camStationId)"
            }
        ]
    )

    print("RECEPTIONS")
    print(tabulate(receptions))

    print("TRANSMISSIONS")
    print(tabulate(transmissions))

    total_receptions = 0
    for _, _, vec_cpt in receptions:
        total_receptions += vec_cpt
    
    total_transmissions = 0
    for _, _, vec_cpt in transmissions:
        total_transmissions += vec_cpt

    print(f"# total transmissions: {total_transmissions} / # total receptions: {total_receptions}")

def get_all_nodes(db_path: str):
    # pattern = r'\w+\.node\[\d+\]$'

    manager = DBManager(db_path=db_path)

    # get all the elements in the table VECTOR and select vectorId and moduleName
    data = manager.select(
        tables={
            "from_": {
                "table": "vector"
            }
        },
        fields_to_select=[
            {
                "table": "vector",
                "column": "vectorId"
            },
            {
                "table": "vector",
                "column": "moduleName"
            },
            {
                "table": "vector",
                "column": "vectorName"
            }
        ]
    )
    print(tabulate(data))

    # get all the node numbers x as in World.node[x]
    for vectorId, moduleName, vectorName in data:
        node_num = int(find_substring_between_elements(moduleName, "[", "]"))
        pass






def main(args):
    if args.db is not None:
        compare_transmission_reception(args.db)
    elif args.db_folder is not None:
        pass
    else:
        print("ERROR - no attribute to find the database(s) is valid.")

args = parser.parse_args()
if __name__ == '__main__':
    main(args)