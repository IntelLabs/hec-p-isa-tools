import argparse
import io
import os
import pathlib
import subprocess
import yaml

from assembler.common.constants import Constants
from assembler.common.run_config import RunConfig
import he_prep as preproc
import he_as as asm

# module constants
DEFAULT_OPERATIONS = Constants.OPERATIONS[:6]

class GenRunConfig(RunConfig):
    """
    Maintains the configuration data for the run.
    """

    SCHEMES = [ 'bgv', 'ckks' ]
    DEFAULT_SCHEME = SCHEMES[0]

    __initialized = False # specifies whether static members have been initialized
    # contains the dictionary of all configuration items supported and their
    # default value (or None if no default)
    __default_config = {}

    def __init__(self, **kwargs):
        """
        Constructs a new GenRunConfig Object from input parameters.

        See base class constructor for more arguments.

        Parameters
        ----------
        N: int
            Ring dimension: PMD = 2^N.

        min_nrns: int
            Minimum number of residuals.

        max_nrns: int
            Maximum number of residuals.

        key_nrns: int
            Optional number of residuals for relinearization keys. Must be greater than `max_nrns`.
            If missing, the `key_nrns` for each P-ISA kernel generated will be set to the kernel
            `nrns` (number of residuals) + 1.

        scheme: str
            FHE Scheme to use. Must be one of the schemes in `GenRunConfig.SCHEMES`.
            Defaults to `GenRunConfig.DEFAULT_SCHEME`.

        op_list: list[str]
            Optional list of name of operations to generate. If provided, it must be a non-empty
            subset of `Constants.OPERATIONS`.
            Defaults to `DEFAULT_OPERATIONS`.

        output_dir: str
            Optional directory where to store all intermediate files and final output.
            This will be created if it doesn't exists.
            Defaults to <current_working_dir>/lib.

        Raises
        ------
        TypeError
            A mandatory configuration value was missing.

        ValueError
            At least, one of the arguments passed is invalid.
        """

        self.__init_statics()

        super().__init__(**kwargs)

        for config_name, default_value in self.__default_config.items():
            assert(not hasattr(self, config_name))
            setattr(self, config_name, kwargs.get(config_name, default_value))
            if getattr(self, config_name) is None:
                raise TypeError(f'Expected value for configuration `{config_name}`, but `None` received.')

        if self.scheme not in self.SCHEMES:
            raise ValueError('Invalid acheme "{}". Expected one of {}'.format(self.scheme, self.SCHEMES))

        for op in self.op_list:
            if op not in Constants.OPERATIONS:
                raise ValueError('Invalid operation in input list of ops "{}". Expected one of {}'.format(op, Constants.OPERATIONS))

        if self.key_nrns > 0:
            if self.key_nrns < self.max_nrns:
                raise ValueError(('`key_nrns` must be greater than `max_nrns` when present. '
                                  'Received {}, but expected greater than {}.').format(self.key_nrns,
                                                                                       self.max_nrns))

    @classmethod
    def __init_statics(cls):
        if not cls.__initialized:
            cls.__default_config["N"]          = None
            cls.__default_config["min_nrns"]   = None
            cls.__default_config["max_nrns"]   = None
            cls.__default_config["key_nrns"]   = 0
            cls.__default_config["scheme"]     = cls.DEFAULT_SCHEME
            cls.__default_config["output_dir"] = os.path.join(pathlib.Path.cwd(), "lib")
            cls.__default_config["op_list"]    = DEFAULT_OPERATIONS

            cls.__initialized = True

    def __str__(self):
        """
        Returns a string representation of the configuration.
        """
        self_dict = self.as_dict()
        with io.StringIO() as retval_f:
            for key, value in self_dict.items():
                print("{}: {}".format(key, value), file=retval_f)
            retval = retval_f.getvalue()
        return retval

    def as_dict(self) -> dict:
        retval = super().as_dict()
        tmp_self_dict = vars(self)
        retval.update({ config_name: tmp_self_dict[config_name] for config_name in self.__default_config })
        return retval

def main(config: GenRunConfig,
         b_verbose: bool = False):

    lib_dir = config.output_dir

    # create output directory to store outputs (if it doesn't already exist)
    pathlib.Path(lib_dir).mkdir(exist_ok = True, parents=True)

    # point to the HERACLES-SEAL-isa-mapping repo
    home_dir = pathlib.Path.home()
    mapping_dir = os.getenv("HERACLES_MAPPING_PATH", os.path.join(home_dir, "HERACLES/HERACLES-SEAL-isa-mapping"))
    # command to run the mapping script to generate operations kernels for our input
    #generate_cmd = 'python3 "{}"'.format(os.path.join(mapping_dir, "kernels/run_he_op.py"))
    generate_cmd = ['python3', '{}'.format(os.path.join(mapping_dir, "kernels/run_he_op.py"))]

    assert config.N < 1024
    assert config.min_nrns > 1
    assert (config.key_nrns == 0 or config.key_nrns > config.max_nrns)
    assert(all(op in Constants.OPERATIONS for op in config.op_list))

    pdegree = 2 ** config.N
    regenerate_string = ""
    for op in config.op_list:
        for rn_el in range(config.min_nrns, config.max_nrns + 1):
            key_nrns = config.key_nrns if config.key_nrns > 0 else rn_el + 1
            regenerate_string = ""
            print("{} {} {} {} {}".format(config.scheme, op, config.N, rn_el, key_nrns))
            output_prefix = "t.{}.{}.{}".format(rn_el, op, config.N)
            basef = os.path.join(lib_dir, output_prefix)
            generate_cmdln = generate_cmd + [ str(x) for x in (config.scheme, op, pdegree, rn_el, key_nrns) ]

            csvfile = basef + ".csv"
            memfile = basef + ".tw.mem"

            # call the external script to generate the kernel for this op
            print(' '.join(generate_cmdln))
            run_result = subprocess.run(generate_cmdln, stdout=subprocess.PIPE)
            if run_result.returncode != 0:
                raise RuntimeError('Exit code: {}. Failure to complete kernel generation successfully.'.format(run_result.returncode))

            # interpret output into correct kernel and mem files
            merged_output = run_result.stdout.decode().splitlines()
            with open(csvfile, 'w') as fout_csv:
                with open(memfile, 'w') as fout_mem:
                    for s_line in merged_output:
                        if s_line:
                            if s_line.startswith('dload') \
                               or s_line.startswith('dstore'):
                                print(s_line, file=fout_mem)
                            else:
                                print(s_line, file=fout_csv)

            # pre-process kernel

            # generate twiddle factors for this kernel
            basef = basef + ".tw" #use the newly generated twiddle file
            print()
            print("Preprocessing")
            preproc.main(basef + ".csv",
                         csvfile,
                         b_verbose=b_verbose)

            # prepare config for assembler
            asm_config = asm.AssemblerRunConfig(input_file=basef + ".csv",
                                                input_mem_file=memfile,
                                                output_prefix=output_prefix,
                                                **config.as_dict()) # convert config to a dictionary and expand it as arguments
            print()
            print("Assembling")
            # run the assembler for this file
            asm.main(asm_config, verbose=b_verbose)

            print(f'Completed "{output_prefix}"')
            print()

def parse_args():
    parser = argparse.ArgumentParser(description=("Generates a collection of HE operations based on input configuration."),
                                     epilog=("To use, users should dump a default configuration file. Edit the file to "
                                             "match the needs for the run, then execute the program with the modified "
                                             "configuration. Note that dumping on top of an existing file will overwrite "
                                             "its contents."))
    parser.add_argument("config_file", help=("YAML configuration file."))
    parser.add_argument("--dump", action="store_true",
                        help=("A default configuration will be writen into the file specified by `config_file`. "
                              "If the file already exists, it will be overwriten."))
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true",
                        help="If enabled, extra information and progress reports are printed to stdout.")
    args = parser.parse_args()

    return args

def readYAMLConfig(input_filename: str):
    """
    Reads in a YAML file and returns a GenRunConfig object parsed from it.
    """
    retval_dict = {}
    with open(input_filename, "r") as infile:
        retval_dict = yaml.safe_load(infile)

    return GenRunConfig(**retval_dict)

def writeYAMLConfig(output_filename: str, config: GenRunConfig):
    """
    Outputs the specified configuration to a YAML file.
    """
    with open(output_filename, "w") as outfile:
        yaml.dump(vars(config), outfile, sort_keys=False)

if __name__ == "__main__":
    module_name = os.path.basename(__file__)
    print(module_name)
    print()

    args = parse_args()

    if args.dump:
        print("Writing default configuration to")
        print(" ", args.config_file)
        default_config = GenRunConfig(N=15, min_nrns=2, max_nrns=18)
        writeYAMLConfig(args.config_file, default_config)
    else:
        print("Loading configuration file:")
        print(" ", args.config_file)
        config = readYAMLConfig(args.config_file)
        print()
        print("Gen Run Configuration")
        print("=====================")
        print(config)
        print("=====================")
        print()
        main(config,
             b_verbose=args.verbose)

    print()
    print(module_name, "- Complete")
