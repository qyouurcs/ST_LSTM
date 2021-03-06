

CUDA_VISIBLE_DEVICES=1 python train_lstm_va.py --model_path ./models_lstm_va_h100_3layers \
    --data_dir ./data/NTURGBD/skeletons_3d_sub_center_train \
    --data_dir_test ./data/NTURGBD/skeletons_3d_sub_center_train_val \
    --input_size 75 \
    --seq_len 10 \
    --ds NTU \
    --hidden_size 100 \
    --num_class 60 \
    --use_bias \
    --log_step 100 \
    --eval_step 200 \
    --save_step 1000 \
    --batch_size 256 \
    --num_epochs 200 \
    --num_workers 4
