@echo off
set mine_root=D:\GreenSoftware\paddleocr_toolkit\
set venv_path=%mine_root%run_dir\paddleocr_env
set inference_path=%mine_root%run_dir\inference
set rec_char_dict_path=%mine_root%run_dir\ppocr_keys_v1.txt

set path=%venv_path%;%venv_path%\Scripts;%path%

@REM python %~dp0image2svghtml.py --det_model_dir="%inference_path%/ch_ppocr_server_v2.0_det_infer/"  --rec_model_dir="%inference_path%/ch_ppocr_server_v2.0_rec_infer/" --cls_model_dir="%inference_path%/ch_ppocr_mobile_v2.0_cls_infer/" --rec_char_dict_path="%rec_char_dict_path%" --use_angle_cls=True --use_space_char=True --use_gpu=False --input_path=%1 --output_path=%2 --dpi_scale=%3
python %~dp0image2originhtml.py --det_model_dir="%inference_path%/ch_ppocr_server_v2.0_det_infer/"  --rec_model_dir="%inference_path%/ch_ppocr_server_v2.0_rec_infer/" --cls_model_dir="%inference_path%/ch_ppocr_mobile_v2.0_cls_infer/" --rec_char_dict_path="%rec_char_dict_path%" --use_angle_cls=True --use_space_char=True --use_gpu=False --input_path=%1 --output_path=%2 --dpi_scale=%3