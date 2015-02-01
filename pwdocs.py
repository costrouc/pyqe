"""
Contains all of the default key documentation.
Moving to module so that I can one day make this work
with the already done documentation (autoupdating then)
"""

def addDocsToKeys(name, keys):
    """Adds doc strings to key info lists
    """
    doc_map = {
        "CONTROL": control_doc,
        "SYSTEM": system_doc
        }

    namelist_doc = doc_map.get(name)
    if not namelist_doc:
        error_str = "unknown namelist {0} unable to add docs"
        raise Exception(error_str.format(name))
    else:
        for key, info  in keys.items():
            key_doc = namelist_doc.get(key)
            if not key_doc:
                error_str = "not documentation for key '{0}'"
                raise Exception(error_str.format(key))
            else:
                info.append(key_doc)


system_doc = {
    'ibrav': """
""",
    'celldm(i)': """
""",
    'A': """
""",
    'B': """
""",
    'C': """
""",
    'cosAB': """
""",
    'cosAC': """
""",
    'cosBC': """
""",
    'nat': """
""",
    'ntyp': """
""",
    'nbnd': """
""",
    'tot_charge': """
""",
    'tot_magnetization': """
""",
    'starting_magnetization(i)': """
""",
    'ecutwfc': """
""",
    'ecutrho': """
""",
    'ecutfock': """
""",
    'nr1': """
""",
    'nr2': """
""",
    'nr3': """
""",
    'nr1s': """
""",
    'nr2s': """
""",
    'nr3s': """
""",
    'nosym': """
""",
    'nosym_evc': """
""",
    'noinv': """
""",
    'no_t_rev': """
""",
    'force_symmorphic': """
""",
    'use_all_frac': """
""",
    'occupations': """
""",
    'one_atom_occupations': """
""",
    'starting_spin_angle': """
""",
    'degauss': """
""",
    'smearing': """
""",
    'nspin': """
""",
    'noncolin': """
""",
    'ecfixed': """
""",
    'qcutz': """
""",
    'q2sigma': """
""",
    'input_dft': """
""",
    'exx_fraction': """
""",
    'screening_parameter': """
""",
    'exxdiv_treatment': """
""",
    'x_gamma_extrapolation': """
""",
    'ecutvcut': """
""",
    'nqx1': """
""",
    'nqx2': """
""",
    'nqx3': """
""",
    'lda_plus_u': """
""",
    'lda_plus_u_kind': """
""",
    'Hubbard_U(i)': """
""",
    'Hubbard_J0(i)': """
""",
    'Hubbard_alpha(i)': """
""",
    'Hubbard_beta(i)': """
""",
    'Hubbard_J(i,ityp)': """
""",
    'starting_ns_eigenvalue(m,ispin,I)': """
""",
    'U_projection_type': """
""",
    'edir': """
""",
    'emaxpos': """
""",
    'eopreg': """
""",
    'eamp': """
""",
    'angle1(i)': """
""",
    'angle2(i)': """
""",
    'constrained_magnetization': """
""",
    'fixed_magnetization(i)': """
""",
    'lambda': """
""",
    'report': """
""",
    'lspinorb': """
""",
    'assume_isolated': """
""",
    'esm_bc': """
""",
    'esm_w': """
""",
    'esm_efield': """
""",
    'esm_nfit': """
""",
    'vdw_corr': """
""",
    'london': """
""",
    'london_s6': """
""",
    'london_rcut': """
""",
    'xdm': """
""",
    'xdm_a1': """
""",
    'xdm_a2': """
""",
    'space_group': """
""",
    'uniqueb': """
""",
    'origin_choice': """
""",
    'rhombohedral': """
"""
}


control_doc = {
    'calculation': """
A string describing the task to be performed
vc = variable cell
""",
    'title': """
reprinted on output
""",
    'verbosity': """
Currently two verbosity levels are implemented:
'high' and 'low'. 'debug' and 'medium' have the same
effect as 'high'; 'default' and 'minimal', as 'low'
""",
    'restart_mode': """
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
""",
    'wf_collect': """
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
""",
    'nstep': """
number of ionic + electronic steps
""",
    'iprint': """
band energies are written every "iprint" iterations
""",
    'tstress': """
calculate stress. It is set to True automatically if
calculation='vc-md' or 'vc-relax'
""",
    'tprnfor': """
calculate forces. It is set to .TRUE. automatically if
calculation='relax','md','vc-md'
""",
    'dt': """
time step for molecular dynamics, in Rydberg atomic units
(1 a.u.=4.8378 * 10^-17 s : beware, the CP code uses
 Hartree atomic units, half that much!!!)
""",
    'outdir': """
input, temporary, output files are found in this directory,
see also "wfcdir"
""",
    'wfcdir': """
this directory specifies where to store files generated by
each processor (*.wfc{N}, *.igk{N}, etc.). Useful for
machines without a parallel file system: set "wfcdir" to
a local file system, while "outdir" should be a parallel
or networkfile system, visible to all processors. Beware:
in order to restart from interrupted runs, or to perform
further calculations using the produced data files, you
may need to copy files to "outdir". Works only for pw.x.
""",
    'prefix': """
prepended to input/output filenames:
prefix.wfc, prefix.rho, etc.
""",
    'lkpoint_dir': """
If .false. a subdirectory for each k_point is not opened
in the "prefix".save directory; Kohn-Sham eigenvalues are
stored instead in a single file for all k-points. Currently
doesn't work together with "wf_collect"
""",
    'max_seconds': """
jobs stops after "max_seconds" CPU time. Use this option
in conjunction with option "restart_mode" if you need to
split a job too long to complete into shorter jobs that
fit into your batch queues. Default is 150 days.
""",
    'etot_conv_thr': """
convergence threshold on total energy (a.u) for ionic
minimization: the convergence criterion is satisfied
when the total energy changes less than "etot_conv_thr"
between two consecutive scf steps. Note that "etot_conv_thr"
is extensive, like the total energy.
See also "forc_conv_thr" - both criteria must be satisfied
""",
    'forc_conv_thr': """
convergence threshold on forces (a.u) for ionic minimization:
the convergence criterion is satisfied when all components of
all forces are smaller than "forc_conv_thr".
See also "etot_conv_thr" - both criteria must be satisfied
""",
    'disk_io': """
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
""",
    'pseudo_dir': """
directory containing pseudopotential files
""",
    'tefield': """
If True a saw-like potential simulating an electric field
is added to the bare ionic potential. See variables "edir",
"eamp", "emaxpos", "eopreg" for the form and size of
the added potential.
""",
    'dipfield': """
If True and tefield=True a dipole correction is also
added to the bare ionic potential - implements the recipe
of L. Bengtsson, PRB 59, 12301 (1999). See variables "edir",
"emaxpos", "eopreg" for the form of the correction. Must
be used ONLY in a slab geometry, for surface calculations,
with the discontinuity FALLING IN THE EMPTY SPACE.
""",
    'lelfield': """
If .TRUE. a homogeneous finite electric field described
through the modern theory of the polarization is applied.
This is different from "tefield=.true." !
""",
    'nberrycyc': """
In the case of a finite electric field  ( lelfield == .TRUE. )
it defines the number of iterations for converging the
wavefunctions in the electric field Hamiltonian, for each
external iteration on the charge density
""",
    'lorbm': """
If .TRUE. perform orbital magnetization calculation.
If finite electric field is applied (lelfield=.true.)
only Kubo terms are computed
[for details see New J. Phys. 12, 053032 (2010)].
The type of calculation is 'nscf' and should be performed
on an automatically generated uniform grid of k points.
Works ONLY with norm-conserving pseudopotentials.
""",
    'lberry': """
If .TRUE. perform a Berry phase calculation
See the header of PW/src/bp_c_phase.f90 for documentation
""",
    'gdir': """
For Berry phase calculation: direction of the k-point
strings in reciprocal space. Allowed values: 1, 2, 3
1=first, 2=second, 3=third reciprocal lattice vector
For calculations with finite electric fields
(lelfield==.true.) "gdir" is the direction of the field
""",
    'nppstr': """
For Berry phase calculation: number of k-points to be
calculated along each symmetry-reduced string
The same for calculation with finite electric fields
(lelfield=.true.)
"""}

