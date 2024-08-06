import ezdxf
import json
import sys


def print_dxf_stat(filepath, layers):
    doc = ezdxf.readfile(filepath)
    msp = doc.modelspace()

    entities = {}
    for entity in msp:
        layer = entity.dxf.layer
        if layer not in entities:
            entities[layer] = {}

        entity_type = entity.dxftype()
        if entity_type not in entities[layer]:
            entities[layer][entity_type] = {}

        line_type = entity.dxf.linetype
        if line_type not in entities[layer][entity_type]:
            entities[layer][entity_type][line_type] = 1
        else:
            entities[layer][entity_type][line_type] += 1

    if layers is None:
        print(json.dumps(entities, indent=4, sort_keys=True, ensure_ascii=False))
    else:
        entities_filtered = {}
        for layer in entities.keys():
            if layer in layers:
                entities_filtered[layer] = entities[layer]
        print(json.dumps(entities_filtered, indent=4, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        print_dxf_stat(sys.argv[1], sys.argv[2:])
    elif len(sys.argv) == 2:
        print_dxf_stat(sys.argv[1], None)
    else:
        print("Usage: python 0.check_dxf.py <dxf_file> [name_of_layers]")
        sys.exit(1)
