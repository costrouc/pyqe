""" 
A module for reading the output and input to Quantum Espresso

read_out_file - reads stdout from pw.x 
read_data_file - reads save file specified in `outfile` from pw.x

other functions are helper functions
"""
import re
import os
import struct
import numpy as np
import xml.etree.ElementTree as ET

# heavily used regex written once to prevent typos
double_regex = r'[-+]?\d+\.\d+(?:[eE][-+]?\d+)?'
int_regex = '[+-]?\d+'


def qe_xml_tag_value(tag):
    """
    This function assumes that the tag's text holds a
    string, vector, (vector, matrix, constant) of either int or float.
    Helps to read quantum espresso "special" xml specification
    """
    _type = tag.attrib.get("type")
    size = int(tag.attrib.get("size", 1))
    col = int(tag.attrib.get("columns", 1))

    if _type == "character":
        value =  tag.text
    elif _type == "real":
        value = np.array(
            [float(_) for _ in re.findall(double_regex, tag.text)])
        if size == 1:
            value = value[0]
        else:
            value.shape = [size / col, col]
    elif _type == "integer":
        value = np.array(
            [int(_) for _ in re.findall(int_regex, tag.text)])
        if size == 1:
            value = value[0]
        else:
            value.shape = [size / col, col]
    elif _type == "logical":
        if 'F' in tag.text:
            value = False
        else:
            value = True
    else:
        error_str = "Type {0} qe xml conversion not supported"
        raise Exception(error_str.format(_type))

    return value


def read_out_file(output_str):
    """
    This functions takes the output file and breaks it into chunks for
    easier parsing. After file is broken into chunks functions are
    used to parse the section for information 

    """
    # Determine if a force/stress/normal calculation was done
    # a differnt regex much be used for each type... I know right?!?!
    if re.search("entering subroutine stress \.\.\.", output_str):
        scf_block_regex = re.compile(
            (
                "Self-consistent Calculation"
                ".+?"
                "total\s+stress\s+\(Ry/bohr\*\*3\)\s+\(kbar\)\s+P=\s*{0}\s+"
                "\s+{0}\s+{0}\s+{0}\s+{0}\s+{0}\s+{0}\s+"
                "\s+{0}\s+{0}\s+{0}\s+{0}\s+{0}\s+{0}\s+"
                "\s+{0}\s+{0}\s+{0}\s+{0}\s+{0}\s+{0}\s+"
            ).format(double_regex),
            re.DOTALL)
    elif re.search("Forces acting on atoms \(Ry/au\):", output_str): 
        scf_block_regex = re.compile(
            (
                "Self-consistent Calculation"
                ".+?"
                "Total force =\s+{0}\s+Total SCF correction =\s+{0}"
            ).format(double_regex),
            re.DOTALL)
    else:
        scf_block_regex = re.compile(
            r"Self-consistent Calculation"
            r".+?"
            r"convergence has been achieved in\s+\d+ iterations",
            re.DOTALL)

    header_regex = re.compile(
        r".+?"
        r"Largest temporary arrays",
        re.DOTALL)

    bfgs_regex = re.compile(
        "BFGS Geometry Optimization"
        ".+?"
        "End of BFGS Geometry Optimization",
        re.DOTALL)

    bands_regex = re.compile(
        "Band Structure Calculation"
        ".+?"
        "End of band structure calculation",
        re.DOTALL)

    md_regex = re.compile(
        "Molecular Dynamics Calculation"
        ".+?"
        "End of molecular dynamics calculation",
        re.DOTALL)

    md_block_regex = re.compile(
        "Entering Dynamics:"
        ".+?"
        "Writing output data file",
        re.DOTALL)

    bfgs_block_regex = re.compile(
        "number of scf cycles"
        ".+?"
        "Writing output data file",
        re.DOTALL)

    final_bfgs_block_regex = re.compile(
        "Final enthalpy"
        ".+?"
        "End final coordinates",
        re.DOTALL)

    footer_regex = re.compile(
        "init_run     :"
        ".+?$",
        re.DOTALL)

    header_str = output_str[:header_regex.search(output_str).end()]
    footer_str = output_str[footer_regex.search(output_str).start():]

    results = {"header": read_out_header(header_str),
               "footer": footer_str}

    # vc-relax or relax calculation (BFGS)
    if bfgs_regex.search(output_str):
        scf_steps = scf_block_regex.findall(output_str)
        bfgs_steps = bfgs_block_regex.findall(output_str)
        bfgs_steps.append(final_bfgs_block_regex.search(output_str).group())

        calc_steps = [ _ for _ in zip(scf_steps, bfgs_steps)]

        results.update({"calculation": read_out_calculation(calc_steps)})
    # md
    elif md_regex.search(output_str):
        scf_steps = scf_block_regex.findall(output_str)
        md_steps = md_block_regex.findall(output_str)
        md_steps.append(output_str[md_regex.search(output_str).end():footer_regex.search(output_str).start()])

        calc_steps = [ _ for _ in zip(scf_steps, md_steps)]

        results.update({"calculation": read_out_calculation(calc_steps)})
    elif bands_regex.search(output_str):
        # bands calculation does not do any scf or itteration calculations
        pass
    # Regular SCF Run
    else:
        scf_step = scf_block_regex.findall(output_str)
        assert len(scf_step) == 1
        results.update({"calculation": read_out_scf(scf_step[0])})

    return results


def read_out_header(header_str):
    """Reader the header of the output file generated by pw.x

    # To shorten regular expressions
    # {0} -> double_regex
    # {1} -> int_regex

    Out of the header many pieces of information are
    collected. Hopefully I can make a restart file from the output

    """

    header_values = {
        "bravais-lattice index": (
            r"bravais-lattice index\s+=\s+({1})", float),
        "lattice parameter": (
            r"lattice parameter \(alat\)\s+=\s+({0}) a\.u\.", float),
        "volume": (
            r"unit-cell volume\s+=\s+({0}) \(a\.u\.\)\^3", float),
        "number atoms/cell": (
            r"number of atoms/cell\s+=\s+({1})", int),
        "number atom types": (
            r"number of atomic types\s+=\s+({1})", int),
        "number electrons": (
            r"number of electrons\s+=\s+({0})", float),
        "number of Kohn Sham states": (
            r"number of Kohn Sham states\s*=\s+({1})", int),
        "kinetic-energy cutoff": (
            r"kinetic-energy cutoff\s+=\s+({0})\s+Ry", float),
        "charge density cutoff": (
            r"charge density cutoff\s+=\s+({0})\s+Ry", float),
        "convergence threshold": (
            r"convergence threshold\s+=\s+({0})", float),
        "mixing beta": (
            r"mixing beta\s+=\s+({0})", float),
        "nstep": (
            r"nstep\s+=\s=({1})", int),
        "celldm": (
            r"celldm\(1\)=\s+({0})\s+"
            r"celldm\(2\)=\s+({0})\s+"
            r"celldm\(3\)=\s+({0})\s+"
            r"celldm\(4\)=\s+({0})\s+"
            r"celldm\(5\)=\s+({0})\s+"
            r"celldm\(6\)=\s+({0})", float),
        "crystal axes": (
            r"a\(1\)\s+=\s+\(\s+({0})\s+({0})\s+({0})\s+\)\s+"
            r"a\(2\)\s+=\s+\(\s+({0})\s+({0})\s+({0})\s+\)\s+"
            r"a\(3\)\s+=\s+\(\s+({0})\s+({0})\s+({0})\s+\)\s+", float),
        "reciprocal axes": (
            r"b\(1\)\s+=\s+\(\s+({0})\s+({0})\s+({0})\s+\)\s+"
            r"b\(2\)\s+=\s+\(\s+({0})\s+({0})\s+({0})\s+\)\s+"
            r"b\(3\)\s+=\s+\(\s+({0})\s+({0})\s+({0})\s+\)\s+", float),
        "FFT dimensions": (
            r"FFT dimensions:\s+\(\s+({1}),\s+({1}),\s+({1})\)", int),
    }

    # Find all keypairs specified above
    header = {}
    for key, (regex, _type) in header_values.items():
        match = re.search(regex.format(double_regex, int_regex), header_str)
        if match:
            if len(match.groups()) == 1:
                header.update({key: _type(match.groups()[0])})
            else:
                header.update({key: [_type(_) for _ in match.groups()]})

    # Atom positions
    atom_pos_regex = "({1})\s+([A-Z][a-z]?)\s+tau\(\s+({1})\s*\)\s+=\s+\(\s+({0})\s+({0})\s+({0})\s+\)"
    matches = re.findall(
        atom_pos_regex.format(double_regex, int_regex),
        header_str)

    atom_positions = []
    for match in matches:
        atom_positions.append([int(match[0]), match[1], [float(match[3]), float(match[4]), float(match[5])]])
    header.update({"atom positions": atom_positions})

    # KPoints
    kpoint_regex = "k\(\s+({1})\)\s+=\s+\(\s+({0})\s+({0})\s+({0})\), wk = \s+({0})"
    matches = re.findall(
        kpoint_regex.format(double_regex, int_regex),
        header_str)

    kpoints = []
    for match in matches:
        kpoints.append([match[0], [match[1], match[2], match[3]], match[4]])
    header.update({"kpoints": kpoints})

    return header


def read_out_scf(scf_block):
    """Reads information from scf step"""
    total_energy_regex = r"!\s+total energy\s+=\s+({0}) Ry".format(double_regex)

    force_regex = r"atom\s+({1})\s+type\s+({1})\s+force\s+=\s+({0})\s+({0})\s+({0})".format(double_regex, int_regex)

    stress_regex = (
        "total\s+stress\s+\(Ry/bohr\*\*3\)\s+\(kbar\)\s+P=\s*{0}\s+"
        "\s+({0})\s+({0})\s+({0})\s+{0}\s+{0}\s+{0}\s+"
        "\s+({0})\s+({0})\s+({0})\s+{0}\s+{0}\s+{0}\s+"
        "\s+({0})\s+({0})\s+({0})\s+{0}\s+{0}\s+{0}\s+"
    ).format(double_regex)

    scf_step = {}

    match = re.search(total_energy_regex, scf_block)
    scf_step.update({"total energy": float(match.group(1))})

    match = re.findall(force_regex, scf_block)
    if match:
        force = [[int(f[0]), int(f[1]), [float(f[2]), float(f[3]), float(f[4])]] for f in match]
        scf_step.update({'forces': force})

    match = re.search(stress_regex, scf_block)
    if match:
        stress = [ float(_) for _ in match.groups(1)]
        scf_step.update({"stress": [stress[0:3],
                                    stress[3:6],
                                    stress[6:9]]})
    return scf_step


def read_out_iteration(iteration_block):
    """Reads the itterations step
    vc-relax, relax, md
    """
    volume_regex = r"new unit-cell volume\s=\s+({0}) a\.u\.\^3".format(double_regex)
    lattice_regex = (
        r"CELL_PARAMETERS.*"
        r"\s+({0})\s+({0})\s+({0})"
        r"\s+({0})\s+({0})\s+({0})"
        r"\s+({0})\s+({0})\s+({0})"
    ).format(double_regex)
    ion_position_regex = "([A-Z][a-z]?)\s+({0})\s+({0})\s+({0})".format(double_regex)

    iteration_step = {}

    match = re.search(volume_regex, iteration_block)
    if match:
        iteration_step.update({"volume": float(match.group(1))})

    match = re.search(lattice_regex, iteration_block)
    lattice = None
    if match:
        lattice = [float(_) for _ in match.groups(1)]
        iteration_step.update({"lattice": [lattice[0:3],
                                           lattice[3:6],
                                           lattice[6:9]]})

    match = re.findall(ion_position_regex, iteration_block)
    if match:
        iteration_step.update({"ion positions": [[_[0], float(_[1]), float(_[2]), float(_[3])] for _ in match]})

    return iteration_step


def read_out_calculation(iteration_steps):
    """Reads information about the calculation from the output file

    - total energy (obviously the developers put an '!' so they could grep this line easier what a hack)  
    - forces on each atom
    - stress of cell
    - volume of cell at each bfgs step
    - lattice vectors at each bfgs step
    - ion positions at each bfgs step
    """

    iterations = []
    for scf_block, iteration_block in iteration_steps:
        iteration = {}

        iteration.update(read_out_scf(scf_block))
        iteration.update(read_out_iteration(iteration_block))

        iterations.append(iteration)

    calculation = {}
    calculation.update({"iterations": iterations})
    calculation.update(iterations[-1])

    return calculation


def read_data_file(inputfile):
    """Reads `data-file.xml` file.

    Returns a data structure with all the information about the saved run.
    Some things are not provided in this file such as the total energy
    which is available in the output file.

    *Not all values are read in because I have not needed them.*

    TAGS:
    Not Implemeneted:
    HEADER, CONTROL, IONS, SYMMETRIES, ELECTRIC-FIELD, PLANE-WAVES
    SPIN, MAGNETIZATION-INIT, OCCUPATIONS, BRILLOUIN-ZONE, PARRALLELISM, 
    EIGENVECTORS

    Implemented:
    CHARGE-DENSITY, EIGENVALUES, EXCHANGE-CORRELATION, BAND-STRUCTURE-INFO
    """
    tree = ET.parse(inputfile)
    root = tree.getroot()

    data = {}

    # TAG: BAND-STRUCTURE-INFO
    bs_tag = root.find("BAND_STRUCTURE_INFO")
    data.update({'band-structure-info': {
        "number kpoints": qe_xml_tag_value(bs_tag.find("NUMBER_OF_K-POINTS")),
        "number spin-components": qe_xml_tag_value(bs_tag.find("NUMBER_OF_SPIN_COMPONENTS")),
        "non-colinear calculation": qe_xml_tag_value(bs_tag.find("NON-COLINEAR_CALCULATION")),
        "number atomic wfc": qe_xml_tag_value(bs_tag.find("NUMBER_OF_ATOMIC_WFC")),
        "number bands": qe_xml_tag_value(bs_tag.find("NUMBER_OF_BANDS")),
        "number electrons": qe_xml_tag_value(bs_tag.find("NUMBER_OF_ELECTRONS")),
        "fermi-energy": qe_xml_tag_value(bs_tag.find("FERMI_ENERGY"))
    }})

    # TAG: EXCHANGE-CORRELATION
    exchange_tag = root.find("EXCHANGE_CORRELATION")
    data.update({"exchange-correlation": re.search("[A-Z\-]+", qe_xml_tag_value(exchange_tag.find("DFT"))).group()})

    # TAG: CHARGE-DENSITY
    charge_density_file = root.find("CHARGE-DENSITY").attrib.get("iotk_link")
    data.update({"charge-density": read_charge_density_file(
            os.path.dirname(inputfile) + '/' + charge_density_file)})

    # TAG: EIGENVALUES (Really K-Point information)
    eigenvalues_tag = root.find("EIGENVALUES")
    kpoints = []
    for eigenvalue_tag in eigenvalues_tag:
        kpoint = {
            "coordinate": qe_xml_tag_value(eigenvalue_tag.find("K-POINT_COORDS")),
            "weight": qe_xml_tag_value(eigenvalue_tag.find("WEIGHT")),
        }

        eigenvalue_file = eigenvalue_tag.find("DATAFILE").attrib.get("iotk_link")
        kpoint.update(read_eigenvalue_file(
            os.path.dirname(inputfile) + '/' + eigenvalue_file))

        kpoints.append(kpoint)
    data.update({"kpoints": kpoints})

    return data


def read_charge_density_file(inputfile):
    """
    Reads charge-density.dat file generated by a quantum espresso
    scf/relax/vc-relax run

    Charge Density file format:
    <z.\d+ ... > zaxis_charge_slice </z.\d+>

    zaxis_charge_slice
        12 bytes - header (I dont know what it is yet)
        nr1*nr2 doubles (8 bytes each)
        24 bytes - footer (I dont know what it is yet)

    Why on earth did they make Charge density a binary/xml file?!?
    """
    f = open(inputfile, "rb")
    charge_xml_str = f.read()

    info_regex = b'<INFO nr1="(\d+)" nr2="(\d+)" nr3="(\d+)"/>'

    match = re.search(info_regex, charge_xml_str)
    nr1, nr2, nr3 = [int(_.decode()) for _ in match.groups()]

    nrz_regex = (
        r'<z\.(\d+) type="(\w+)" size="(\d+)" kind="(\d+)">\n'
        r'.{{12}}(.{{{0}}}).{{24}}'
        r'\n    </z\.\d+>\n'
    ).format(nr1*nr2*8)

    matches = re.findall(nrz_regex.encode(), charge_xml_str, re.DOTALL)

    data = []
    for nrz, _type, size, kind, byte_str in matches:
        data += struct.unpack("d"*nr1*nr2, byte_str)

    charge_data = np.array(data, order='F', ndmin=3)
    charge_data.shape = [nr1, nr2, nr3]
    return charge_data

def read_eigenvalue_file(inputfile):
    """Reads the output files for kpoints generated by pw.x
    returns a dictionary of the occupations

    """
    tree = ET.parse(inputfile)
    root = tree.getroot()

    eigenvalues = [float(_) for _ in
                   re.findall(double_regex, root.find('EIGENVALUES').text)]
    occupations = [float(_) for _ in
                   re.findall(double_regex, root.find('OCCUPATIONS').text)]

    return {"eigenvalues": eigenvalues,
            "occupations": occupations}
