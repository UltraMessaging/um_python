#!/bin/sh

LBM_INSTALL_PATH=$1
INPUT_LBM_H_FILE="$LBM_INSTALL_PATH/include/lbm/lbm.h"
OUTPUT_DIR=`pwd`
LBM_PERL_SCRIPT=$OUTPUT_DIR/lbm_h_py.pl
LBM_PY_BUILDER_FILE=$OUTPUT_DIR/lbmwrapper.py
LBM_PY_CALLBACK_FILE=$OUTPUT_DIR/lbm_py_callback.h

check_error_exit (){
	 
	if [ $? -ne 0 ];then
		echo "Cannot continue processing, error occured"
		exit 1
	fi
}


check_error_file_exit (){

	if [ $? -ne 0 ] || ! [ -e $1 ];then
		echo "Cannot continue processing, error occured"
		exit 1
	fi
}

check_input (){

	#if file or directory does not exist then exit
	if ! [ -e $INPUT_LBM_H_FILE ];then
		echo "$INPUT_LBM_H_FILE does not exist"
		exit 1
	fi

	if ! [ -e $LBM_PERL_SCRIPT ];then
		echo "$LBM_PERL_SCRIPT does not exist"
		exit 1
	fi
}

prepare_lbm_h (){

	echo "Resolving macros and removing #include from $INPUT_LBM_H_FILE..."
	echo "perl $LBM_PERL_SCRIPT < $INPUT_LBM_H_FILE > $1"
	perl $LBM_PERL_SCRIPT < $INPUT_LBM_H_FILE > $1
	check_error_file_exit $1
}

gcc_preprocess (){

	echo "Preprocessing $1 ..."
	cmd=`echo "gcc -dD -E  -P -undef -fdirectives-only -o $2 $1"`
	echo $cmd
	`$cmd`
	check_error_file_exit $2
}

clean_lbm_h (){

	echo "Cleaning the input file..."

	#remove all LBMExpDLL
	echo "sed -i 's/LBMExpDLL//g' $1"
	sed -i 's/LBMExpDLL//g' $1
	check_error_exit

	#remove functions that are missing from some versions of UM
	echo "sed -i \"/\b\(lbm_auth_set_credentials\|lbm_auth_set_credentials\|lbm_authstorage_close_storage_xml\|lbm_authstorage_user_del_role\|lbm_authstorage_load_roletable\|lbm_authstorage_unload_roletable\|lbm_authstorage_user_add_role\|lbm_authstorage_print_roletable\|lbm_authstorage_addtpnam\|lbm_authstorage_deltpnam\|lbm_authstorage_checkpermission\|lbm_authstorage_open_storage_xml\|lbm_authstorage_roletable_add_role_action\|lbm_hfx_attr_create_default\|lbm_hfx_attr_dup\)\b/d\" $1"
	sed -i "/\b\(lbm_auth_set_credentials\|lbm_auth_set_credentials\|lbm_authstorage_close_storage_xml\|lbm_authstorage_user_del_role\|lbm_authstorage_load_roletable\|lbm_authstorage_unload_roletable\|lbm_authstorage_user_add_role\|lbm_authstorage_print_roletable\|lbm_authstorage_addtpnam\|lbm_authstorage_deltpnam\|lbm_authstorage_checkpermission\|lbm_authstorage_open_storage_xml\|lbm_authstorage_roletable_add_role_action\|lbm_hfx_attr_create_default\|lbm_hfx_attr_dup\)\b/d" $1

	#extract all the #define into another file
	echo "grep -e '#define' $1 > $2"
	grep -e '#define' $1 > $2

	#remove all the #define which cannot be parsed by CFFI (no numbers in them)
	echo "sed -i \"/#define.*[0-9].*/!d\" $2"
	sed -i "/#define.*[0-9].*/!d" $2

	#remove LBM_VERS as it cannot be parsed
	echo "sed -i \"/\\bLBM_VERS\\b/d\" $2"
	sed -i "/\bLBM_VERS\b/d" $2

	#Workaround for bug http://meltdown.29west.com/bugzilla/show_bug.cgi?id=10557
	echo "#define LBTIPC_BEHAVIOR_RCVR_PACED 0" >> $2
	echo "#define LBTIPC_BEHAVIOR_SRC_PACED 1" >> $2	

	#remove all the #defines from original header file
	echo "sed -i \"/#define/d\" $1"
	sed -i "/#define/d" $1
}

generate_py_builder (){
	echo "Generating LBM python builder file..."

	echo "from cffi import FFI" > $LBM_PY_BUILDER_FILE
	echo "ffibuilder = FFI()" >> $LBM_PY_BUILDER_FILE
	echo "" >> $LBM_PY_BUILDER_FILE

	#read the macro file to include in the cdef
	echo "with open('$1') as f:" >> $LBM_PY_BUILDER_FILE
	echo -e "\tffibuilder.cdef(f.read())" >> $LBM_PY_BUILDER_FILE
	echo "" >> $LBM_PY_BUILDER_FILE

	echo "with open('$2') as f:" >> $LBM_PY_BUILDER_FILE
	echo -e "\tffibuilder.cdef(f.read())" >> $LBM_PY_BUILDER_FILE
	echo "" >> $LBM_PY_BUILDER_FILE

	#check if callback is available and callbacks are defined
	if [ -e $LBM_PY_CALLBACK_FILE ];then
		echo "with open('$LBM_PY_CALLBACK_FILE') as f:" >> $LBM_PY_BUILDER_FILE
		echo -e "\tffibuilder.cdef(f.read())" >> $LBM_PY_BUILDER_FILE
		echo "" >> $LBM_PY_BUILDER_FILE
	fi

	echo "ffibuilder.set_source(\"_lbm_cffi\"," >> $LBM_PY_BUILDER_FILE
	echo "\"\"\""  >> $LBM_PY_BUILDER_FILE
	#Workaround for bug 10557
	echo -e "\t #define LBTIPC_BEHAVIOR_RCVR_PACED 0" >> $LBM_PY_BUILDER_FILE
	echo -e "\t #define LBTIPC_BEHAVIOR_SRC_PACED 1" >> $LBM_PY_BUILDER_FILE

	echo -e "\t #include \"lbm.h\"" >> $LBM_PY_BUILDER_FILE
	echo "\"\"\"," >> $LBM_PY_BUILDER_FILE
	echo -e "\tlibraries=['lbm']," >> $LBM_PY_BUILDER_FILE
	echo -e "\tinclude_dirs=['$LBM_INSTALL_PATH/include/lbm'],"  >> $LBM_PY_BUILDER_FILE
	echo -e "\tlibrary_dirs=['$LBM_INSTALL_PATH/lib'])" >> $LBM_PY_BUILDER_FILE
	echo "" >> $LBM_PY_BUILDER_FILE

	echo "if __name__ == \"__main__\":" >> $LBM_PY_BUILDER_FILE
	echo -e "\tffibuilder.compile(verbose=True)" >> $LBM_PY_BUILDER_FILE

}

usage (){

	echo "Usage: $1 UM_platform_path"
	echo "Example: $1 ../UMQ_6.10.1/Linux-glibc-2.5-x86_64"
}

main (){

	#if less arguments are passed then exit
	if [ "$#" -ne 1 ];then
		usage $0
		exit 1
	fi

	#Step 0: Sanitize 
	check_input

	#Step 1: Remove all the #include
	LBM_NO_INCLUDE_FILE=$OUTPUT_DIR/lbm_no_include.h
	prepare_lbm_h $LBM_NO_INCLUDE_FILE 


	#Step 2: preprocess lbm.h
	LBM_PREPROCESSED_FILE=$OUTPUT_DIR/lbm_processed.h
	gcc_preprocess $LBM_NO_INCLUDE_FILE $LBM_PREPROCESSED_FILE

	#Step 3: remove the unwanted #defines and functions
	LBM_MACRO_FILE=$OUTPUT_DIR/lbm_macro.h
	clean_lbm_h $LBM_PREPROCESSED_FILE $LBM_MACRO_FILE 

	#Step 4: generate the lbm python builder script
	generate_py_builder $LBM_MACRO_FILE $LBM_PREPROCESSED_FILE

	#Step 5: build the lbm python wrapper
	echo "Building lbm python wrapper..."
	echo "python $LBM_PY_BUILDER_FILE"
	python $LBM_PY_BUILDER_FILE
	check_error_exit

}

#Let's Start !!
main $*
