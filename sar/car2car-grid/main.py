import xml.etree.ElementTree as ET
import os
import argparse

parser = argparse.ArgumentParser(
    prog="SAR SUMO config generator"
)
parser.add_argument('-n', '--net_file', type=str, help='Path to the net file for the .sumo.cfg file.')


SUMOCFG_EXT = ".sumo.cfg"
ROU_EXT = ".rou.xml"
TRIPS_EXT = ".trips.xml"


def create_folder(new_folder: str) -> None:
    folder_content = os.listdir()
    if new_folder not in folder_content:
        os.mkdir(new_folder)
        print(f"Folder {new_folder} created.")
    else:
        print(f"Folder {new_folder} already existing.")

def create_sumocfg(template_path: str, config_name: str, vec_path: str, net_path: str):
    base_sumocfg_tree = ET.parse(template_path)
    base_sumocfg_root = base_sumocfg_tree.getroot()

    # modify input > net-file "value" and input > route-files "value"
    for input in base_sumocfg_root.iter("input"):
        for net_file in input.iter("net-file"):
            net_file.set("value", net_path)
        for route_files in input.iter("route-files"):
            route_files.set("value", vec_path)
    
    base_sumocfg_tree.write(f"{config_name}/grid{SUMOCFG_EXT}")

def create_routes(base_routes_xml: str, modulo: int, config_name: str) -> str:
    # find all the ids in the base routes file
    base_routes_tree = ET.parse(base_routes_xml)
    base_routes_root = base_routes_tree.getroot()
    indexes_routes_to_remove = []
    for index_r in range(len(base_routes_root.findall('vehicle'))):
        if index_r % modulo != 0:
            indexes_routes_to_remove.append(index_r)
    # reverse the list of indexes to delete in order to modify 
    # the xml tree without modifying the indexes
    indexes_routes_to_remove.reverse()

    # read the xml base files
    base_routes_root = base_routes_tree.getroot()
    for index_r in indexes_routes_to_remove:
        base_routes_root.remove(base_routes_root[index_r])

    gen_route_xml = f"{config_name}/routes{ROU_EXT}"
    base_routes_tree.write(gen_route_xml)

    return f"routes{ROU_EXT}"

def create_trips(base_trips_xml: str, modulo: int, config_name: str) -> str:
    # find all the indexes in the base trips file
    base_trips_tree = ET.parse(base_trips_xml)
    base_trips_root = base_trips_tree.getroot()
    indexes_trips_to_remove = []
    for index_t in range(len(base_trips_root.findall("trip"))):
        if index_t % modulo != 0:
            indexes_trips_to_remove.append(index_t)
    # reverse the list of indexes to delete in order to modify 
    # the xml tree without modifying the indexes
    indexes_trips_to_remove.reverse()

    base_trips_root = base_trips_tree.getroot()   
    for index_t in indexes_trips_to_remove:
        base_trips_root.remove(base_trips_root[index_t])

    gen_trips_xml = f"{config_name}/trips{TRIPS_EXT}"
    base_trips_tree.write(gen_trips_xml)

    return f"trips{TRIPS_EXT}"

def create_configurations(base_path: str, frequencies: dict, net_path: str) -> None:
    # list the content of the base folder and identify elements based on their extension
    for file in os.listdir(base_path):
        if SUMOCFG_EXT in file:
            base_sumocfg_xml = f"{base_path}{file}"
            print(f"Base sumo configuration file identified as: {base_sumocfg_xml}")
        elif ROU_EXT in file:
            base_routes_xml = f"{base_path}{file}"
            print(f"Base routes configuration file identified as: {base_routes_xml}")
        elif TRIPS_EXT in file:
            base_trips_xml = f"{base_path}{file}"
            print(f"Base trips configuration file identified as: {base_trips_xml}")
        else:
            print(f"Ignoring {file}")
            
    for name, freq in frequencies.items():
        # calculate every which index we should keep in order to have the desired frequency
        modulo = int(1 / freq)

        # create the result folder
        create_folder(name)
        gen_routes_xml = create_routes(base_routes_xml=base_routes_xml, modulo=modulo, config_name=name)
        create_sumocfg(template_path=base_sumocfg_xml, config_name=name, vec_path=gen_routes_xml, net_path=net_path)

def main(args):
    frequencies = {
        "full": 1.0,
        "half": 0.5,
        "quarter": 0.25
    }

    create_configurations('base/', frequencies, args.net_file)


args = parser.parse_args()
if __name__ == '__main__':
    main(args)
    