# 0. Install Dependencies

```
pip3 install ezdxf, open3d, numpy, sklearn
```

# 1. [Optional] Inspect dxf file

In order to parse lines from a dxf file, we need to know the information of the dxf file, such as:

- Entity type: `LINE`(two points line), `LWPOLYLINE`(poly line with more points), and `ARC`;
- Line type: `CONTINUOUS`, `DASHED`, `BYLAYER`(defined by layer), etc.

## 1.1 Run python script

`python3 dxf_check.py <dxf file> [layers...]`

- dxf file: the path to the dxf file
- layers (optional): names of layers you wish to see. If not specified, it will print all
  layers.

For example, to check the information of the dxf file `example.dxf`, with only one layer called `seinä`,
run:

```bash
python3 0.check_dxf.py example.dxf seinä
```

The output will be like:

```json
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

In this result, `LINE` and `LWPOLYLINE` are entity types. `ACAD_ISO03W100`, `ACAD_ISO10W100`, and `BYLAYER` are line
types. The numbers are the counts of each line. So you can check what are the lines you wish to use in the next step.

# 2. Label Walls

## 2.1 [optional] Create a config file to specify entity and line types

The script will use `default.config` by default, if you wish to specify the entity and line types you want to extract,
create a new one with json format.

For example:

- `LINE` with line types `BYLAYER` and `ACAD_ISO03W100`
- `LWPOLYLINE` with line type `BYLAYER`

The config file should be like:

```json
{
  "seinä": {
    "LINE": [
      "BYLAYER",
      "ACAD_ISO03W100"
    ],
    "LWPOLYLINE": [
      "BYLAYER"
    ]
  }
}
```

P.S. `ACAD_ISO10W100` means `ISO dash dot`, `ACAD_ISO03W100` means `ISO dash space`.

## 2.2 Run python script

`python3 label_wall.py <dxf file> <ply_file> [-o out.ply] [-c cfg.config] [-t] [-v]`

Parameters:

- dxf file: the path to the input dxf file
- ply file: the path to the input ply file
- [optional] -o out.ply: the path to the output ply file, if not specified, it will save to the same directory as input
  ply file, with name `{original_name}_label_{number_suffix}`
- [optional] -c cfg.config: the path to the config file, if not specified, it will use `default.config`
- [optional] -t: visualize a quick testing by using only 1% of the point cloud. Not saving the output file.
- [optional] -v: visualize the result after saving labeled file.
- [optional] -d: distance threshold for dxf line to points, default is 0.05, the higher the value, the thicker the wall
  will be labeled.

For example:

With `wall.dxf` and `room.ply`, run:

```bash
python3 1.label_wall.py wall.dxf room.ply
```

With `wall.dxf` and `room.ply`, using `new_cfg_file.config`, run:

```bash
python3 1.label_wall.py wall.dxf room.ply -c new_cfg_file.config
```

# 3. [optional] Inspect the labeled file

Use other software to inspect the labeled file, such as `CloudCompare`. You can see the labeled walls in green color.
Make further modifications manually if needed. To do this:

- Change the color of walls to be green (RGB: 0, 255, 0),
- Change the color of other points to be any other color.

# 4. Convert ply file to npy file

## 4.1 Run python script

```
python3 ply2npy.py <ply file>
```

The script will save the npy file in the same directory as the ply file, with the same name but different extension.

# Todo

- Use another method such as a mask ply file, to prevent overwriting the color.
- `ARC` entity type is not supported yet. Although the code is already in the `label_wall.py`, disabled for not tested.
- In `LWPOLYLINE` entity type, bulge is not supported yet.