#!/bin/bash/

if [ $# -ne 0 ] ; then
    # Add user binaries folder to PATH
    echo "Setting up for user ${1}"
    echo "If you didn't put a '.' before this command, you won't find the yolo CLI"
    
    # Read parameters from config
    parse_yaml() {
        local prefix=$2
        local s='[[:space:]]*' w='[a-zA-Z0-9_]*' fs=$(echo @|tr @ '\034')
            sed -ne "s|^\($s\):|\1|" \
                    -e "s|^\($s\)\($w\)$s:$s[\"']\(.*\)[\"']$s\$|\1$fs\2$fs\3|p" \
                    -e "s|^\($s\)\($w\)$s:$s\(.*\)$s\$|\1$fs\2$fs\3|p"  $1 |
            awk -F$fs '{
                indent = length($1)/2;
                vname[indent] = $2;
                for (i in vname) {if (i > indent) {delete vname[i]}}
                if (length($3) > 0) {
                    vn=""; for (i=0; i<indent; i++) {vn=(vn)(vname[i])("_")}
                    printf("%s%s%s=\"%s\"\n", "'$prefix'",vn, $2, $3);
                }
            }'
    }

    eval $(parse_yaml config.yaml)

    # Create local site package dir and download python dependencies
    mkdir $python_dir
    python3 -c "import sys; sys.path.append(\"${python_dir}\")"
    export PYTHONPATH=$PYTHONPATH:${python_dir}
    check_python_package() {
        local package_name=$1
        python3 -c "import $package_name" &> /dev/null
        if [ $? -ne 0 ]; then
            echo "The package '$package_name' is not installed. Installing ..."
            python3 -m pip install --target=$python_dir $package_name
        else
            echo "The package '$package_name' is installed."
        fi
    }
    check_python_package "ultralytics"
    check_python_package "roboflow"
    check_python_package "utils"
    check_python_package "opencv-python"
    check_python_package "yaml"
    check_python_package "json"
    export PATH=$PATH:${python_dir}bin/

else
    echo "Please enter a username in the form:"
    echo ". user_setup.sh [USERNAME]"
    echo "!!!!!THE DOT BEFORE THE SCRIPT NAME IS IMPORTANT!!!!"
fi