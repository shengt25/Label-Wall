# Install Dependencies

```
pip3 install ezdxf, open3d, numpy, sklearn
```

# 1. [Optional] Inspect dxf file

In order to parse lines from a dxf file, we need to know the information of the dxf file, such as:

- Entity type: `LINE`(two points line), `LWPOLYLINE`(poly line with more points), and `ARC`;
- Line type: `CONTINUOUS`, `DASHED`, `BYLAYER`(defined by layer), etc.

## 1.1 Run python script

```bash
python3 tools/check_dxf.py <dxf_file> [layers...]
```

- dxf file: the path to the dxf file
- layers (optional): names of layers you wish to see. You can enter multiply names split with whitespace. If not
  specified, it will print all
  layers.

For example, to check the information of the dxf file `example.dxf`, with only one layer called `seinä`,
run:

```bash
python3 tools/check_dxf.py example.dxf seinä
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
types. The numbers are the counts of each type of line. So you can check what are the lines you wish to use in the next
step.

# 2. Create Mask for Walls

## 2.1 [optional] Create a config file to specify entity and line types

The script will use `default.config` by default, which will extract `LINE` and `LWPOLYLINE` entity types with line.  
With `default2.config` it will also extract `LINE` and `LWPOLYLINE` entity type, but with line and ISO dash space
line.  
If you wish to specify the entity and line types you want to extract, create a new one with json format.

For example:

- `LINE` with line types `BYLAYER` and `ACAD_ISO03W100`
- `LWPOLYLINE` with line type `BYLAYER`

Entity types:

- 'LINE': Normal line defined by two points,
- 'LWPOLYLINE': Polyline with more points.

Line types:

- `BYLAYER`: `Defined by layer`,
- `ACAD_ISO10W100`: `ISO dash dot`,
- `ACAD_ISO03W100`: `ISO dash space`.

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

## 2.2 Run python script

### Basic Usage

```bash
python3 make_mask.py <dxf_file> <ply_file>
```

Parameters:

- dxf_file: the path to the input dxf file
- ply_file: the path to the input ply file

For example:

With `wall.dxf` and `room.ply`, run:

```bash
python3 make_mask.py wall.dxf room.ply
```

### Advanced Usage

Please refer to the help message for more options.

```bash
python3 make_mask.py -h
```

# 3. Create Labeled File

## 3.1 [Optional] Modify the mask

Use other software to inspect the labeled file, such as `CloudCompare`. You can see the labeled walls in green color.
Make further modifications manually if needed. To do this:

- Change the color of walls to be green (RGB: 0, 255, 0),
- Change the color of other points to be any other color, by default light grey.

## 3.2 Run python script

### Basic Usage

```bash
python3 make_npy.py <ply_file> <mask_ply_file>
```

Parameters:
ply_file: the path to the input ply file
mask_ply_file: the path to the input mask ply file

For example:
With `room.ply` and `room_mask.ply`, run:

```bash
python3 make_npy.py room.ply room_mask.ply
```

### Advanced Usage

Please refer to the help message for more options.

```bash
python3 make_npy.py -h
```

# Tool Scripts

## npy2ply.py

Convert npy to ply and mask ply file, in order to easily inspect or modify the labeled npy file. The foreground points
will be colored with green,

```bash
python3 tools/npy2ply.py <npy_file> [fg_label]
```

Parameters:

- npy_file: the path to the input npy file
- fg_label (optional): the label of the foreground points, default is 2.

## visualize_npy.py

Visualize the labeled npy file, with the foreground points in green color. Also with the original point cloud in light
grey next to the labeled one.

```bash
python3 tools/vis_npy.py <npy_file> [fg_label]
```

Parameters:

- npy_file: the path to the input npy file
- fg_label (optional): the label of the foreground points, default is 2.

# Todo

- [x] Use another method such as a mask ply file, to prevent overwriting the color.
- [ ] `ARC` entity type is not supported yet. Although the code is already in the `label_wall.py`, disabled for not
  tested.
- [ ] In `LWPOLYLINE` entity type, bulge is not supported yet.