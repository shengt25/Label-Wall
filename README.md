# [Optional] Check dxf file entity types and line types

In order to parse lines from a dxf file, we need to know the information of the dxf file, such as:  
Entity type: `LINE`(two points line), `LWPOLYLINE`(poly line with more points), and `ARC`;  
Line type: `CONTINUOUS`, `DASHED`, `BYLAYER`(defined by layer), etc.

## Install dependencies

```
pip3 install ezdxf
```

## Run python code

`python3 dxf_check.py <dxf file> [layers...]`
- dxf file: the path to the dxf file
- layers (optional): names of layers you wish to see. If not specified, it will print all
  layers.

For example, to check the information of the dxf file `example.dxf`, with only one layer called `seinä`,
run:
```
python3 dxf_check.py example.dxf seinä
```

The output will be like:

```
{
    "seinä": {
        "LINE": {
            "ACAD_ISO03W100": 26,
            "ACAD_ISO10W100": 7,
            "BYLAYER": 174
        },
        "LWPOLYLINE": {
            "BYLAYER": 1
        }
    }
}

```
In this result, `LINE` and `LWPOLYLINE` are entity types. `ACAD_ISO03W100`, `ACAD_ISO10W100`, and `BYLAYER` are line types. The numbers are the counts of each line. So you can check what are the lines you wish to use in the next step.

# Run label script
## Install dependencies

```
pip3 install ezdxf, open3d, numpy, sklearn
```

## [optional] Create a config file with json format
The script will use `default.config` by default, if you wish to specify the entity and line types you want to extract, create a new one with json format.

For example:  
- `LINE` with line types `BYLAYER` and `ACAD_ISO03W100`
- `LWPOLYLINE` with line type `BYLAYER`

The config file should be like:

```json
{
"seinä": {
     "LINE": ["BYLAYER", "ACAD_ISO03W100"],
     "LWPOLYLINE": ["BYLAYER"]
    }
}
```
P.S. `ACAD_ISO10W100` means `ISO dash dot`, `ACAD_ISO03W100` means `ISO dash space`.

## Run python code

`python3 label_wall.py <dxf file> <ply_file> [-o out.ply] [-c cfg.config] [-t] [-v]`  

Parameters:
- dxf file: the path to the input dxf file
- ply file: the path to the input ply file
- [optional] -o out.ply: the path to the output ply file, if not specified, it will use original file name with `_label` and a number suffix
- [optional] -c cfg.config: the path to the config file, if not specified, it will use `default.config`
- [optional] -t: visualize a quick testing by using only 1% of the point cloud. Not saving the output file.
- [optional] -v: visualize the result after saving labeled file.

For example:

With `wall.dxf` and `room.ply`, run:
```
python3 label_wall.py wall.dxf room.ply
```

With `wall.dxf` and `room.ply`, using `type_1.config`, run:
```
python3 label_wall.py wall.dxf room.ply -c type_1.config
```