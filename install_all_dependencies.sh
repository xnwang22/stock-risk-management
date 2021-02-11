#!/usr/bin/env bash
# -----------------------------------------------------------------------------------
# [SPIL Team] SPIL PyPi bash script
#             Install all Project requirements to virtualenv (default)
#
#             This scripts installs dependencies to a virtual environment.
#             To install to the global (system) site-packages instead,
#             pass the --global flag. To install to a specific path,
#             pass the first argument as the target directory name.
#
#             The following dependencies for Tests are also installed:
#                 - boto3
#                 - pytest, pytest-cov, pytest-html
#                 - pylint
#             If you have additional requirements for your test cases,
#             you can place them in a 'test_requirements.txt' and
#             they will be included in the install process.
#
#
# Usage: source install_all_dependencies.sh [target] [options...]
#
#   -h, --help          Show this help.
#   -g, --global        Install project dependencies to the
#                         global (system) site-packages instead.
#   -U, --upgrade       Upgrade all project dependencies (packages)
#                         to the newest available version. Note that
#                         if a requirement specifies the version
#                         explicitly, such as "package==0.1",
#                         it won't be upgraded.
# -----------------------------------------------------------------------------------

function main()
{
    # ----------
    # Environment
    # ----------
#    local trusted_host='spil-pypi-cloud.np.salespil.xfinity.com'
#    local credentials="spil:${PYPI_PASSWORD:=spil}"
#    local port=443
#    local add_on='simple'
#    local final_url="https://${credentials}@${trusted_host}:${port}/${add_on}/"
#    local test_requirements=(
#      'boto3'
#      'pytest'
#      'pytest-cov'
#      'pytest-html'
#      'pylint'
#      'pygments'
#    )
    local use_virtualenv=true
    local install_options=()
    local target=''
    local ec=''

    # ----------
    # Start script
    # ----------
    go_to_project_dir

    parse_args "$@"

    # Check if arguments passed indicate that the shell script should exit
    # If the script is being sourced, we should return instead
    if [[ -n $ec ]]; then
        [[ $0 = ${BASH_SOURCE[0]} ]] && exit ${ec} || return ${ec}
    fi

    if [[ -n $target ]]; then
        echo "Installing to $target..."
        install_options+=("-t ./${target}")
    elif [[ $use_virtualenv = true ]]; then
        echo "Installing to virtualenv..."
        setup_venv
    else
        echo "Installing to global site-packages..."
        # We should deactivate virtualenv before doing a global install
        # if we detect that it is currently activated
        if [[ -n $VIRTUAL_ENV ]]; then
            echo "INFO: Deactivating virtualenv ..."
            deactivate
        fi
    fi

    declare -a requirements pypi_requirements
    read_project_requirements
    echo
    # Install Base Dependencies
    print_header 'Install Requirements'
    pip install ${requirements[@]} ${install_options[@]}
   
}

# ----------
# Parse command line options
# ----------
function parse_args()
{
    local opt

    while [[ $# -gt 0 ]]; do
        opt="$1"
        shift

        case "$opt" in
            -g|--global)
                use_virtualenv=false
                ;;
            -h|\?|--help)
                show_help
                ec=0; break
                ;;
            -U|--upgrade)
                install_options+=('--upgrade')
                # Use an "eager" update strategy by default; see 'pip --help'.
                install_options+=('--upgrade-strategy=eager')
                ;;
            -*)
                echo "${BASH_SOURCE##*/}: illegal option $opt" >&2
                ec=1; break
                ;;
            *)
                target="$opt"
                ;;
        esac
    done
}

# Show the help for this script (and exit)
# The "help message" is just the comment block at the top of the script
function show_help()
{
    local script_filename="${BASH_SOURCE##*/}"
    local help_text=''
    local line

    while IFS= read -r line; do
        [[ $line != \#* ]] && break
        line=${line#\#?*}; line=${line#\#*}; line="${line//[$'\t\r\n']}"$'\n'
        help_text+="$line"
    done < ${script_filename}

    help_text="${help_text#*-[$'\t\r\n']}"; help_text="${help_text%[$'\t\r\n']?*}"
    echo "$help_text"
}

# Print out a header to the terminal
# Arguments: {1} is the title to print for the header
function print_header()
{
    echo "[[ $1 ]]"
}

# Go to the root project directory, if not already in it
# This is equivalent to the parent directory of this shell script
# Another option is to use basename or dirname, but these are expensive operations that spawn subshells
function go_to_project_dir()
{
    local script_dir="${BASH_SOURCE%/*}"
    [[ -d "$script_dir" ]] && cd "$script_dir"
}

# Setup the virtual environment if it's not currently active
# When running on Jenkins, This function should bypass the need for an OS check
function setup_venv()
{
    if [[ -n $PYTHON36_DIR ]]; then                         # On Jenkins
        if [[ -z $VIRTUAL_ENV ]]; then
            echo 'INFO: Activating virtualenv for Python 3.6...'
            source ${PYTHON36_DIR}/bin/activate
        else
            echo "INFO: Using existing venv in \"${PYTHON36_DIR}\"..."
        fi

    elif [[ -z $VIRTUAL_ENV  ]]; then         # On Local
        echo 'INFO: Setting up virtualenv...'
        set_os
        echo "Operating system is: $os"
        # Create a new virtualenv only if the 'venv' directory doesn't already exist
        if [[ ! -d venv ]]; then
            echo && print_header "Create Virtualenv in 'venv'"
            python3 -m venv venv
        fi

        if [[ "$os" == "WINDOWS" ]]; then
            source venv/Scripts/activate
        else
            source venv/bin/activate
        fi
    fi
}

# Set the env variable "$os" to the name of the current operating system
# The list of possible OS types is partially taken from:
# https://stackoverflow.com/a/29239609/10237506
function set_os()
{
    case "$OSTYPE" in
        *solaris*)                              os="SOLARIS" ;;
        *darwin*)                               os="OSX" ;;
        *linux*)                                os="LINUX" ;;
        *bsd*)                                  os="BSD" ;;
        *msys*|*win32*|*cygwin*)                os="WINDOWS" ;;
        *hurd*|*sua*|*interix*)                 os="GNU";;
        *sunos*|*indiana*|*illumos*|*smartos*)  os="SUN";;
        *)                                      os="unknown: $OSTYPE" ;;
    esac
}

# This will parse the project requirements from "requirements.txt"
# (It will also include "test_requirements.txt", if one exists)
# into the named arrays {requirements, pypi_requirements}
# Note: If you don't declare these arrays before calling the function, they are declared as global variables.
function read_project_requirements()
{
    requirements=()
    pypi_requirements=()

    __parse_requirements_from_file requirements.txt
    [[ -e test_requirements.txt ]] && __parse_requirements_from_file test_requirements.txt
}

# Arguments: {1} is the requirements file name to parse
function __parse_requirements_from_file()
{
    local line

    while IFS='' read -r line || [[ -n $line ]]; do
        line=${line//[$'\t\r\n']}
        if [[ $line != \#* ]]; then
            if [[ $line = tpx[-_]* ]]; then
                pypi_requirements+=($line)
            else
                requirements+=($line)
            fi
        fi
    done < $1
}

main "$@"
