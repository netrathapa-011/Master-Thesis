#!/usr/bin/env pvpython
"""
Generates xdmf file from .h5 miluphcuda/miluphpc output files for Paraview postprocessing.

Authors: Christoph Schäfer, Christoph Burger
Last updated: 30/May/2025
"""

import h5py
import sys
import argparse
import os
import traceback


def parse_args():
    h5files = [f for f in sorted(os.listdir(os.getcwd())) if f.endswith(".h5")]

    parser = argparse.ArgumentParser(
        description=(
            "Generates xdmf file from .h5 miluphcuda/miluphpc output files for Paraview postprocessing. "
            "Open the generated .xdmf file with ParaView."
        )
    )

    parser.add_argument("--output", default="paraview.xdmf")
    parser.add_argument("--dim", default="3")
    parser.add_argument("--miluphpc", action="store_true")
    parser.add_argument("--input_files", nargs="+", default=h5files)
    parser.add_argument("--add_attr", nargs="+")

    return parser.parse_args()


def write_xdmf_header(fh):
    fh.write(
        """<Xdmf>
<Domain Name="MSI">
<Grid Name="CellTime" GridType="Collection" CollectionType="Temporal">
"""
    )


def write_xdmf_footer(fh):
    fh.write(
        """</Grid>
</Domain>
</Xdmf>
"""
    )


if __name__ == "__main__":
    args = parse_args()

    with open(args.output, "w") as xdmfh:
        write_xdmf_header(xdmfh)

        try:
            f0 = h5py.File(args.input_files[0], "r")
        except IOError:
            sys.exit("Cannot open first HDF5 file.")

        if args.miluphpc:
            possible_attributes = [
                "Sxx", "Sxy", "Syy", "cs", "dSdtxx", "dSdtxy", "dSdtyy",
                "drhodt", "e", "localStrain", "m", "noi", "p", "proc",
                "rho", "sml"
            ]
        else:
            possible_attributes = [
                "aneos_T", "aneos_cs", "aneos_entropy", "aneos_phase_flag",
                "rho", "p", "e", "m", "local_strain", "material_type",
                "soundspeed", "sml", "sml_initial", "number_of_interactions",
                "tree_depth", "cs_min", "e_min", "p_min", "rho_min",
                "cs_max", "e_max", "p_max", "rho_max",
                "deviatoric_stress", "DIM_root_of_damage_tensile",
                "number_of_activated_flaws", "alpha_jutzi",
                "DIM_root_of_damage_porjutzi", "damage_total",
                "total_plastic_strain"
            ]

        wanted_attributes = [a for a in possible_attributes if a in f0]
        f0.close()

        if args.add_attr:
            wanted_attributes.extend(args.add_attr)

        for hfile in args.input_files:
            with h5py.File(hfile, "r") as f:
                t = f["time"][0]
                n = len(f["x"])

                xdmfh.write('<Grid Name="particles" GridType="Uniform">\n')
                xdmfh.write(f'<Time Value="{t}" />\n')
                xdmfh.write(f'<Topology TopologyType="Polyvertex" NodesPerElement="{n}"/>\n')

                xdmfh.write('<Geometry GeometryType="XYZ">\n')
                xdmfh.write(f'<DataItem DataType="Float" Precision="8" Dimensions="{n} 3" Format="HDF">\n')
                xdmfh.write(f"{hfile}:/x\n</DataItem>\n</Geometry>\n")

                xdmfh.write('<Attribute Name="velocity" AttributeType="Vector" Center="Node">\n')
                xdmfh.write(f'<DataItem DataType="Float" Dimensions="{n} {args.dim}" Format="HDF">\n')
                xdmfh.write(f"{hfile}:/v\n</DataItem>\n</Attribute>\n")

                for attr in wanted_attributes:
                    if attr == "deviatoric_stress":
                        d = int(args.dim) ** 2
                        xdmfh.write('<Attribute Name="deviatoric_stress" AttributeType="Tensor" Center="Node">\n')
                        xdmfh.write(f'<DataItem DataType="Float" Dimensions="{n} {d}" Format="HDF">\n')
                        xdmfh.write(f"{hfile}:/{attr}\n</DataItem>\n</Attribute>\n")
                    else:
                        dtype = "Integer" if attr in {
                            "noi", "proc", "material_type",
                            "number_of_interactions",
                            "number_of_activated_flaws",
                            "aneos_phase_flag"
                        } else "Float"

                        xdmfh.write(f'<Attribute Name="{attr}" AttributeType="Scalar" Center="Node">\n')
                        xdmfh.write(f'<DataItem DataType="{dtype}" Dimensions="{n} 1" Format="HDF">\n')
                        xdmfh.write(f"{hfile}:/{attr}\n</DataItem>\n</Attribute>\n")

                xdmfh.write("</Grid>\n")

        write_xdmf_footer(xdmfh)

    print(f"Done. Processed {len(args.input_files)} files.")

