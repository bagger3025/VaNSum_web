# $1 date ex) 1101  main의 now 바꾸어서 실행할 것!
export MKL_SERVICE_FORCE_INTEL=1
nohup python main.py -task make_train_data -n_cpus 28 -now $1_0000> make_train_data_$1.out &
