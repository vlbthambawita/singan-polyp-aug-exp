from singan_polyp_aug import style_transfer
import os
from PIL import Image
import torch


generated_img_dir = "/work/vajira/DATA/sinGAN_polyps/singan_out"
real_img_dir = "/home/vajira/data/singan_polyp_checkpoints/real_images"

out_dir = "/work/vajira/DATA/sinGAN_polyps/singan_out_style_transfered_1_to_1_vgg16"
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

style_transfer.transfer_style_to_folder(generated_img_dir, real_img_dir,  out_dir, 1000, content_weight=1, style_weight=1, device = device, vgg_model="vgg16")