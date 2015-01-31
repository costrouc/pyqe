"""
Namelist

These are dictionaries with configuration varaibles.
"""
import os

def isPositive(value):
    return value > 0.0

def defaultNStep(control):
    if control.keypairs.get('calculation') in ['scf', 'nscf']:
        return 1
    else:
        return 50

def defaultTprnfor(control):
    return control.keypairs.get('calculation') in ['vc-md', 'vc-relax']

def defaultOutdir(control):
    return os.environ.get('ESPRESSO_TMPDIR', './')

def defaultPseudoDir(control):
    return os.environ.get('ESPRESSO_PSEUDODIR',
                          os.environ.get('HOME') + '/espresso/pseudo/')

def defaultDiskIO(control):
    if control.keypairs.get('calculation') == 'scf':
        return 'low'
    else:
        return 'medium'


class Control:
    """
    General variables for controlling the run

    The keys tuple:
    key-name | type | default value | available values (may be function) | doc string for key
    """
    keys = {
        'calculation': (str, 'scf', ('scf', 'nscf', 'bands', 'relax', 'md', 'vc-relax'), """
A string describing the task to be performed
vc = variable cell
"""),
        'title': (str, '', (), """
reprinted on output
"""),
        'verbosity': (str, 'low', ('low', 'high'), """
Currently two verbosity levels are implemented:
  'high' and 'low'. 'debug' and 'medium' have the same
  effect as 'high'; 'default' and 'minimal', as 'low'
"""),
        'restart_mode': ( str, 'from_scratch', ('from_scratch', 'restart'), """
'from_scratch'  : from scratch. This is the normal way
                  to perform a PWscf calculation
'restart'       : from previous interrupted run. Use this
                  switch only if you want to continue an
                  interrupted calculation, not to start a
                  new one, or to perform non-scf calculations.
                  Works only if the calculation was cleanly
                  stopped using variable "max_seconds", or
                  by user request with an "exit file" (i.e.:
                  create a file "prefix".EXIT, in directory
                  "outdir"; see variables "prefix", "outdir")
"""),
        'wf_collect': (bool, False, (), """
This flag controls the way wavefunctions are stored to disk :

True    collect wavefunctions from all processors, store them
        into the output data directory "outdir"/"prefix".save,
        one wavefunction per k-point in subdirs K000001/,
        K000001/, etc.. Use this if you want wavefunctions
        to be readable on a different number of processors.

False   do not collect wavefunctions, leave them in temporary
        local files (one per processor). The resulting format
        will be readable only by jobs running on the same
        number of processors and pools. Requires less I/O
        than the previous case.

Note that this flag has no effect on reading, only on writing.
"""),
        'nstep': (int, defaultNStep, (), """
number of ionic + electronic steps
"""),
        'iprint': (int, None, (), """
band energies are written every "iprint" iterations
"""),
        'tstress': (bool, False, (), """
calculate stress. It is set to True automatically if
calculation='vc-md' or 'vc-relax'
"""),
        'tprnfor': (bool, defaultTprnfor , (), """
calculate forces. It is set to .TRUE. automatically if
calculation='relax','md','vc-md'
"""),
        'dt': (float, 20.0, isPositive, """
time step for molecular dynamics, in Rydberg atomic units
(1 a.u.=4.8378 * 10^-17 s : beware, the CP code uses
 Hartree atomic units, half that much!!!)
"""),
        'outdir': (str, defaultOutdir, (), """
input, temporary, output files are found in this directory,
see also "wfcdir"
"""),
        'wfcdir': (str, defaultOutdir, (), """
this directory specifies where to store files generated by
each processor (*.wfc{N}, *.igk{N}, etc.). Useful for
machines without a parallel file system: set "wfcdir" to
a local file system, while "outdir" should be a parallel
or networkfile system, visible to all processors. Beware:
in order to restart from interrupted runs, or to perform
further calculations using the produced data files, you
may need to copy files to "outdir". Works only for pw.x.
"""),
        'prefix': (str, 'pwscf', (), """
prepended to input/output filenames:
prefix.wfc, prefix.rho, etc.
"""),             
        'lkpoint_dir': (bool, True, (), """
If .false. a subdirectory for each k_point is not opened
in the "prefix".save directory; Kohn-Sham eigenvalues are
stored instead in a single file for all k-points. Currently
doesn't work together with "wf_collect"
"""),             
        'max_seconds': (float, 1.0e7, isPositive, """
jobs stops after "max_seconds" CPU time. Use this option
in conjunction with option "restart_mode" if you need to
split a job too long to complete into shorter jobs that
fit into your batch queues. Default is 150 days.
"""),
        'etot_conv_thr': (float, 1.0e-4, isPositive, """
convergence threshold on total energy (a.u) for ionic
minimization: the convergence criterion is satisfied
when the total energy changes less than "etot_conv_thr"
between two consecutive scf steps. Note that "etot_conv_thr"
is extensive, like the total energy.
See also "forc_conv_thr" - both criteria must be satisfied
"""),
        'forc_conv_thr': (float, 1.0e-4, isPositive, """
convergence threshold on forces (a.u) for ionic minimization:
the convergence criterion is satisfied when all components of
all forces are smaller than "forc_conv_thr".
See also "etot_conv_thr" - both criteria must be satisfied
"""),
        'disk_io': (str, defaultDiskIO, ('none', 'low', 'medium', 'high'), """
Specifies the amount of disk I/O activity
'high':   save all data to disk at each SCF step

'medium': save wavefunctions at each SCF step unless
          there is a single k-point per process (in which
          case the behavior is the same as 'low')

'low' :   store wfc in memory, save only at the end

'none':   do not save anything, not even at the end
          ('scf', 'nscf', 'bands' calculations; some data
           may be written anyway for other calculations)

Default is 'low' for the scf case, 'medium' otherwise.
Note that the needed RAM increases as disk I/O decreases!
It is no longer needed to specify 'high' in order to be able
to restart from an interrupted calculation (see "restart_mode")
but you cannot restart in disk_io='none'
"""),
        'pseudo_dir': (str, defaultPseudoDir, (), """
directory containing pseudopotential files             
"""),
        'tefield': (bool, False, (), """
If True a saw-like potential simulating an electric field
is added to the bare ionic potential. See variables "edir",
"eamp", "emaxpos", "eopreg" for the form and size of
the added potential.
"""),
        'dipfield': (bool, False, (), """
If True and tefield=True a dipole correction is also
added to the bare ionic potential - implements the recipe
of L. Bengtsson, PRB 59, 12301 (1999). See variables "edir",
"emaxpos", "eopreg" for the form of the correction. Must
be used ONLY in a slab geometry, for surface calculations,
with the discontinuity FALLING IN THE EMPTY SPACE.
"""),
        'lelfield': (bool, False, (), """
If .TRUE. a homogeneous finite electric field described
through the modern theory of the polarization is applied.
This is different from "tefield=.true." !
"""),
        'nberrycyc': (int, 1, isPositive, """
In the case of a finite electric field  ( lelfield == .TRUE. )
it defines the number of iterations for converging the
wavefunctions in the electric field Hamiltonian, for each
external iteration on the charge density
"""),
             
        'lorbm': (bool, False, (), """
If .TRUE. perform orbital magnetization calculation.
If finite electric field is applied (lelfield=.true.)
only Kubo terms are computed
[for details see New J. Phys. 12, 053032 (2010)].
The type of calculation is 'nscf' and should be performed
on an automatically generated uniform grid of k points.
Works ONLY with norm-conserving pseudopotentials.
"""),             
        'lberry': (bool, False, (), """
If .TRUE. perform a Berry phase calculation
See the header of PW/src/bp_c_phase.f90 for documentation
"""),
        'gdir': (int, None, (1, 2, 3), """
For Berry phase calculation: direction of the k-point
strings in reciprocal space. Allowed values: 1, 2, 3
1=first, 2=second, 3=third reciprocal lattice vector
For calculations with finite electric fields
(lelfield==.true.) "gdir" is the direction of the field
"""),
        'nppstr': (int, None, isPositive, """
For Berry phase calculation: number of k-points to be
calculated along each symmetry-reduced string
The same for calculation with finite electric fields
(lelfield=.true.)
""")}

    def __init__(self):
        self.name = "CONTROL"
        self.keypairs = {}

    def keyDescription(self, key):
        """
        Returns a nicely formated description of the key
        for Espresso calculations
        """
        from collections import Callable
        
        value = Control.keys.get(key)
        
        keydesc_str = ""
        if value:
            keydesc_str = "Key: '{0}'\n".format(key)

            current_keyvalue = self.keypairs.get(key, None)
            keydesc_str += "Current Value\n   {0}\n".format(current_keyvalue)
            keydesc_str += "Type\n   {0}\n".format(value[0].__name__)
            if isinstance(value[1], Callable):
                keydesc_str += """Default:
   Function Name          : {0}
   Current Function Value : {1}
""".format(value[1].__name__, value[1](self))
            else:
                keydesc_str += """Default:
   Value                  : {0}
""".format(value[1])
            if isinstance(value[2], Callable):
                keydesc_str += """Valid Values:
   Function Name          : {0}
   Function (value)       -> (valueValid ? True : False)
""".format(value[1].__name__)
            elif value[2]:
                keydesc_str += "Valid Values\n   " + " ".join(map(str, value[2])) + "\n"
            else:
                keydesc_str += "Valid Values\n   [Full Range]\n"

            keydesc_str += "Description:\n" + value[3]
        else:
            keydesc_str = "Key {0} not a valid CONTROL variable\n".format(key)

        return keydesc_str

    def addKeypair(self, keypair):
        """
        Adds the keypair to the namelist Control
        """
        from collections import Callable
        
        key, value = keypair
        key_info = self.keys.get(key)

        # Check if key is valid
        if not key_info:
            error_str = "{0} {1} not valid key name".format(self.name, key)
            raise Exception(error_str)

        # Check if value is of correct type
        if not isinstance(value, key_info[0]):
            error_str = "{0} key {1} value {2} not of type {3}".format(self.name, key, value, key_info[0].__name__)
            raise Exception(error_str)

        # Check the range of value is correct
        if (isinstance(key_info[2], Callable) and not key_info[2](value)) or (key_info[2] and value not in key_info[2]):
            error_str = "'{0}' key '{1}' value '{2}' invalid range".format(self.name, key, value)
            raise Exception(error_str)

        # Check if user is setting key to its default value (harmless)
        if ((isinstance(key_info[1], Callable) and
             value == key_info[1](self)) or value == key_info[1]):
            print("Warning: Setting Key '{0}' to its default value".format(key))

        if self.keypairs.get(key):
            print("Warning: Overwritting Key '{0}'".format(key))

        self.keypairs[key] = value