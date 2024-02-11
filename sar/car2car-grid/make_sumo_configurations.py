import xml.etree.ElementTree as ET
import os
import argparse
import copy


parser = argparse.ArgumentParser(
    prog="SAR SUMO config generator"
)
parser.add_argument(
    '-n', 
    '--net_file', 
    type=str, 
    help='Path to the net file for the .sumo.cfg file.'
)

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
    print("Generating SUMO configuration file ...")
    base_sumocfg_tree = ET.parse(template_path)
    base_sumocfg_root = base_sumocfg_tree.getroot()

    # modify input > net-file "value" and input > route-files "value"
    for input in base_sumocfg_root.iter("input"):
        for net_file in input.iter("net-file"):
            net_file.set("value", net_path)
        for route_files in input.iter("route-files"):
            route_files.set("value", vec_path)
    
    base_sumocfg_tree.write(f"{config_name}/grid{SUMOCFG_EXT}")
    print(f"SUMO configuration file created.")

def create_routes(base_routes_xml: str, frequency: float, config_name: str) -> str:
    # find all the ids in the base routes file
    base_routes_tree = ET.parse(base_routes_xml)
    base_routes_root = base_routes_tree.getroot()

    # find how many times to duplicate the elements
    base_number_vehicles = len(base_routes_root.findall('vehicle'))
    total_number_vehicles = int(base_number_vehicles * frequency)
    print(f"Frequency: {frequency}Hz / base # of vehicles: {base_number_vehicles} / total # of vehicles: {total_number_vehicles}")

    # if frequency > 1 : duplicate vehicules and append them at the end
    if frequency > 1:
        for index_v in range(base_number_vehicles, total_number_vehicles, 1):
            new_v = copy.deepcopy(base_routes_root[index_v % base_number_vehicles])
            new_v.set("id", str(index_v))
            base_routes_root.append(new_v)

    # if frequency < 1 : remove vehicules
    elif frequency < 1:
        for index_v in range(base_number_vehicles - 1, total_number_vehicles - 2, -1):
            base_routes_root.remove(base_routes_root[index_v])

    # change times of apparition
    time_apparition_step = 1 / frequency
    departure_time = 0
    for vehicle in base_routes_root.iter('vehicle'):
        print(f"ID vehicle: {vehicle.get('id')} / Depart time: {departure_time} s")
        vehicle.set("depart", str(departure_time))
        departure_time += time_apparition_step
        

    gen_route_xml = f"{config_name}/route{ROU_EXT}"
    base_routes_tree.write(gen_route_xml)
    print(f"Route file generated at {gen_route_xml}")

    return f"route{ROU_EXT}"

def create_configurations(base_path: str, frequencies: dict, net_path: str) -> None:
    # list the content of the base folder and identify elements based on their extension
    for file in os.listdir(base_path):
        if SUMOCFG_EXT in file:
            base_sumocfg_xml = f"{base_path}{file}"
            print(f"Base sumo configuration file identified as: {base_sumocfg_xml}")
        elif ROU_EXT in file:
            base_routes_xml = f"{base_path}{file}"
            print(f"Base routes configuration file identified as: {base_routes_xml}")
        else:
            print(f"Ignoring {file}")
            
    for name, freq in frequencies.items():
        print(f"Configuration name: {name} / # cars per s: {freq}")
        # create the result folder
        create_folder(name)
        # create the routes for the simulation
        gen_routes_xml = create_routes(base_routes_xml=base_routes_xml, frequency=freq, config_name=name)
        # create sumo config file to use the generate routes
        create_sumocfg(template_path=base_sumocfg_xml, config_name=name, vec_path=gen_routes_xml, net_path=net_path)
        print("Configuration generated.")

def main(args):
    # frequencies at which the vehicles should appear on the map
    frequencies = {
        "16Hz": 16.0,
        "8Hz": 8.0,
        "4Hz": 4.0,
        "2Hz": 2.0,
        "1Hz": 1.0,
        "0.5Hz": 0.5,
        "0.25Hz": 0.25
    }
    # create the configurations for every frequencies given
    create_configurations('base/', frequencies, args.net_file)
    print("All sumo configurations have been generated for the sar project.")


args = parser.parse_args()
if __name__ == '__main__':
    main(args)
    