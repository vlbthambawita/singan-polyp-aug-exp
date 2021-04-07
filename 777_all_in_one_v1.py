#=========================================================
# Developer: Vajira Thambawita
# Reference: https://github.com/meetshah1995/pytorch-semseg
#=========================================================



import argparse
from datetime import datetime
import os
import copy
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np


#Pytorch
import torch
import torch.optim as optim
from torch.optim import lr_scheduler
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import models, transforms,datasets, utils
from torchvision.utils import save_image
from torch.utils.tensorboard import SummaryWriter
from torch.autograd import Variable
from torchsummary import summary

import segmentation_models_pytorch as smp


from data.dataset import Dataset
from data.prepare_data import prepare_data, prepare_test_data
#from data import PolypsDatasetWithGridEncoding
#from data import PolypsDatasetWithGridEncoding_TestData
import pyra_pytorch as pyra
from utils import dice_coeff, iou_pytorch, visualize

import segmentation_models_pytorch as smp


#======================================
# Get and set all input parameters
#======================================

parser = argparse.ArgumentParser()

# Hardware
#parser.add_argument("--device", default="gpu", help="Device to run the code")
parser.add_argument("--device_id", type=int, default=0, help="")

# Optional parameters to identify the experiments
parser.add_argument("--exp_name", type=str, help="A name to identify the experiment", required=True)
#parser.add_argument("--py_file",default=os.path.abspath(__file__)) # store current python file


# Directory and file handling
parser.add_argument("--train_CSVs", 
                    nargs="+",
                    default=None,
                    help="CSV file list with image and mask paths")

parser.add_argument("--val_CSVs",
                    nargs="+",
                    default=None,
                    help="CSV file list with image and mask paths")

parser.add_argument("--test_CSVs",
                    nargs="+",
                    default=None,
                    help="CSV file list with image and mask paths")

parser.add_argument("--out_dir", 
                    default="/work/vajira/DATA/sinGAN_polyps/sinGAN_exp_out/checkpoints",
                    help="Main output dierectory")

parser.add_argument("--tensorboard_dir", 
                    default="/work/vajira/DATA/sinGAN_polyps/sinGAN_exp_out/tensorboard",
                    help="Folder to save output of tensorboard")

parser.add_argument("--test_out_dir",
                   default= "/work/vajira/DATA/sinGAN_polyps/sinGAN_exp_out/test_samples",
                   help="Output folder for testing data"
)    

parser.add_argument("--best_checkpoint_name", type=str, default="best_checkpoint.pth", help="A name to save bet checkpoint")

parser.add_argument("--img_size", type=int, default=128, help="Image height and width to resize")


# Action handling 
parser.add_argument("--num_epochs", type=int, default=1, help="Numbe of epochs to train")
parser.add_argument("--start_epoch", type=int, default=0, help="start epoch of training")
parser.add_argument("--num_test_samples", type=int, default=5, help="Number of samples to test.")

# smp parameters
parser.add_argument("--model", help="The model to perform segmentation", required=True)
parser.add_argument("--encoder", type=str, default='se_resnext50_32x4d', help="smp encoders")
parser.add_argument("--encoder_weights", type=str, default='imagenet', help="encoder weights")
parser.add_argument("--classes", default=[0,255], help="classes per pixel")
parser.add_argument("--activation", type=str, default='softmax2d', help="last activation layers activation")

#PYRA
parser.add_argument("--pyra", type=bool, default=False, help="To enable PYRA grid encoding.")
parser.add_argument("--grid_sizes_train", type=list, default=[256], help="Grid sizes to use in training")
parser.add_argument("--grid_sizes_val", type=list, default=[256], help="Grid sizes to use in training")
parser.add_argument("--grid_sizes_test", type=list, default=[256], help="Grid sizes to use in testing")
parser.add_argument("--in_channels", type=int, default=3, help="Number of input channgels")

# Parameters
parser.add_argument("--bs", type=int, default=8, help="Mini batch size")
parser.add_argument("--val_bs", type=int, default=1, help="Batch size")
parser.add_argument("--lr", type=float, default=0.0001, help="Learning rate for training")
parser.add_argument("--lr_change_point", type=int, default=50, help="After this point LR will be changed.")


parser.add_argument("--num_workers", type=int, default=12, help="Number of workers in dataloader")
parser.add_argument("--weight_decay", type=float, default=1e-5, help="weight decay of the optimizer")
parser.add_argument("--lr_sch_factor", type=float, default=0.1, help="Factor to reduce lr in the scheduler")
parser.add_argument("--lr_sch_patience", type=int, default=25, help="Num of epochs to be patience for updating lr")


parser.add_argument("--num_samples", type=int, default=5, help="Number of samples to print from validation set")
parser.add_argument("action", type=str, help="Select an action to run", choices=["train", "retrain", "test", "check", "check_val"])
parser.add_argument("--checkpoint_interval", type=int, default=25, help="Interval to save checkpoint models")
#parser.add_argument("--fold", type=str, default="fold_1", help="Select the validation fold", choices=["fold_1", "fold_2", "fold_3"])
#parser.add_argument("--num_test", default= 200, type=int, help="Number of samples to test set from 1k dataset")
#parser.add_argument("--model_path", default="", help="Model path to load weights")
#parser.add_argument("--num_of_samples", default=30, type=int, help="Number of samples to validate (Montecalo sampling)")

opt = parser.parse_args()


#==========================================
# Device handling
#==========================================
torch.cuda.set_device(opt.device_id)
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

opt.device = DEVICE

#===========================================
# Folder handling
#===========================================

#make output folder if not exist
os.makedirs(opt.out_dir, exist_ok=True)


# make subfolder in the output folder 
#py_file_name = opt.py_file.split("/")[-1] # Get python file name (soruce code name)
CHECKPOINT_DIR = os.path.join(opt.out_dir, opt.exp_name + "/checkpoints")
os.makedirs(CHECKPOINT_DIR, exist_ok=True)

# make tensorboard subdirectory for the experiment
tensorboard_exp_dir = os.path.join(opt.tensorboard_dir, opt.exp_name)
os.makedirs( tensorboard_exp_dir, exist_ok=True)

#==========================================
# Tensorboard
#==========================================
# Initialize summary writer
writer = SummaryWriter(tensorboard_exp_dir)

#==========================================
# Prepare Data
#==========================================


#================================================
# Train the model
#================================================
def train_model(train_loader, valid_loader, model, loss, metrics, optimizer, opt):

       # create epoch runners 
    # it is a simple loop of iterating over dataloader`s samples
    train_epoch = smp.utils.train.TrainEpoch(
        model, 
        loss=loss, 
        metrics=metrics, 
        optimizer=optimizer,
        device=DEVICE,
        verbose=True,
    )

    valid_epoch = smp.utils.train.ValidEpoch(
        model, 
        loss=loss, 
        metrics=metrics, 
        device=DEVICE,
        verbose=True,
    )



    max_score = 0

    best_chk_path = os.path.join(CHECKPOINT_DIR, opt.best_checkpoint_name)

    for i in range(opt.start_epoch + 1, opt.start_epoch + opt.num_epochs +1 ):
        
        print('\nEpoch: {}'.format(i))
        train_logs = train_epoch.run(train_loader)
        valid_logs = valid_epoch.run(valid_loader)
        
        # do something (save model, change lr, etc.)
        if max_score < valid_logs['iou_score']:
            max_score = valid_logs['iou_score']
            torch.save({"model":model, "epoch": i}, best_chk_path)
            print('Best Model saved!')
            print("Testing....")
            do_test(opt)
            print("Tested")

            
        if i == opt.lr_change_point:
            optimizer.param_groups[0]['lr'] = 1e-5
            print('Decrease decoder learning rate to 1e-5!')

        # writing to logs to tensorboard
        for key, value in train_logs.items():
            writer.add_scalar(f"Train/{key}", value, i)

        for key, value in valid_logs.items():
            writer.add_scalar(f"Valid/{key}", value, i)


    


# update here
    

#==============================================
# Heatmap generator from tensor
#==============================================
def generate_heatmapts(img_tensor):
    print(img_tensor.shape)
    fig_list = []
    for n in range(img_tensor.shape[0]):
        img = img_tensor[n]
        img = img.squeeze(dim=0)
        img_np = img.detach().cpu().numpy()
        #img_np = np.transforms(img_np, (1,2,0))
        
        plt.imshow(img_np, cmap="hot")
        fig = plt.gcf()
        fig_list.append(fig)
        # plt.clf()
        plt.close()

    return fig_list



#===============================================
# Prepare models
#===============================================
def prepare_model(opt):
    # model = UNet(n_channels=4, n_classes=1) # 4 = 3 channels + 1 grid encode

    # create segmentation model with pretrained encoder
    model = getattr(smp, opt.model)(
        encoder_name=opt.encoder,
        in_channels=opt.in_channels, 
        encoder_weights=opt.encoder_weights, 
        classes=len(opt.classes), 
        activation=opt.activation,
    )

    return model

#====================================
# Run training process
#====================================
def run_train(opt):
    model = prepare_model(opt)

    preprocessing_fn = smp.encoders.get_preprocessing_fn(opt.encoder, opt.encoder_weights)

    train_loader, val_loader = prepare_data(opt, preprocessing_fn=None)

    loss = smp.utils.losses.DiceLoss(ignore_channels=[0])

    metrics = [
        smp.utils.metrics.IoU(threshold=0.5, ignore_channels=[0]),
    ]

    optimizer = torch.optim.Adam([ 
        dict(params=model.parameters(), lr=opt.lr),
    ])

    train_model(train_loader, val_loader, model, loss, metrics, optimizer, opt)
#====================================
# Re-train process
#====================================
def run_retrain(opt):

    checkpoint_dict = torch.load(os.path.join(CHECKPOINT_DIR, opt.best_checkpoint_name))

    opt.start_epoch =  checkpoint_dict["epoch"]
    model = checkpoint_dict["model"]

    print("Model epoch:", checkpoint_dict["epoch"])
    print("Model retrain started from epoch:", opt.start_epoch)

    preprocessing_fn = smp.encoders.get_preprocessing_fn(opt.encoder, opt.encoder_weights)

    train_loader, val_loader = prepare_data(opt, preprocessing_fn)

    loss = smp.utils.losses.DiceLoss()

    metrics = [
        smp.utils.metrics.IoU(threshold=0.5),
    ]

    optimizer = torch.optim.Adam([ 
        dict(params=model.parameters(), lr=opt.lr),
    ])

    train_model(train_loader, val_loader, model, loss, metrics, optimizer, opt)

#=====================================
# Check model
#====================================
def check_model_graph():
    raise NotImplementedError


#===================================
# Inference from pre-trained models
#===================================

def do_test(opt):


    checkpoint_dict = torch.load(os.path.join(CHECKPOINT_DIR, opt.best_checkpoint_name))

    test_epoch =  checkpoint_dict["epoch"]
    best_model = checkpoint_dict["model"]

    print("Model best epoch:", test_epoch)

    preprocessing_fn = smp.encoders.get_preprocessing_fn(opt.encoder, opt.encoder_weights)
    test_dataset = prepare_test_data(opt, preprocessing_fn=None)
    test_dataset_vis = prepare_test_data(opt, preprocessing_fn=None)
    
    
    for i in range(opt.num_test_samples):
        image, mask = test_dataset[i]
        image_vis, _ = test_dataset_vis[i]

        #print(image)

        mask_tensor = torch.from_numpy(mask).to(opt.device).unsqueeze(0)

        image_tensor = torch.from_numpy(image).to(opt.device).unsqueeze(0)
        pr_mask = best_model.predict(image_tensor)

        pr_mask = pr_mask.squeeze().cpu().numpy().round()

        fig = visualize(
            input_image_new=np.transpose(image_vis, (1,2,0)).astype(int),
            GT_mask_0=mask[0, :,:],
            Pred_mask_0 = pr_mask[0,:,:],
            GT_mask_1= mask[1,:,:],
            Pred_mask_1 = pr_mask[1, :,:]
        )

        fig.savefig(f"./test_202_{i}.png")
        writer.add_figure(f"Test_sample/sample-{i}", fig, global_step=test_epoch)





def check_test_score(opt):

    

    checkpoint_dict = torch.load(os.path.join(CHECKPOINT_DIR, opt.best_checkpoint_name))

    test_best_epoch =  checkpoint_dict["epoch"]
    best_model = checkpoint_dict["model"]

    print("Model best epoch:", test_best_epoch)
    
    

    preprocessing_fn = smp.encoders.get_preprocessing_fn(opt.encoder, opt.encoder_weights)
    test_dataset = prepare_test_data(opt, preprocessing_fn=None)
    
    test_dataloader = DataLoader(test_dataset, num_workers=48)

    loss = smp.utils.losses.DiceLoss()
    # Testing with two class layers
    metrics = [
        #smp.utils.metrics.IoU(threshold=0.5),
        smp.utils.metrics.IoU(threshold=0.5, ignore_channels=None),
    ]

    test_epoch = smp.utils.train.ValidEpoch(
        model=best_model,
        loss=loss,
        metrics=metrics,
        device=DEVICE,
    )

    logs = test_epoch.run(test_dataloader)
    print("logs=", str(logs))
    writer.add_text(f"{opt.exp_name}-test-score", str(logs), global_step=test_best_epoch)

    # Testing with only class layer 1 (polyps)
    loss = smp.utils.losses.DiceLoss(ignore_channels=[0])
    metrics = [
        #smp.utils.metrics.IoU(threshold=0.5),
        smp.utils.metrics.IoU(threshold=0.5, ignore_channels=[0]),
    ]

    test_epoch = smp.utils.train.ValidEpoch(
        model=best_model,
        loss=loss,
        metrics=metrics,
        device=DEVICE,
    )

    logs = test_epoch.run(test_dataloader)
    print("logs=", str(logs))
    writer.add_text(f"{opt.exp_name}-test-score-ignore-channel-0", str(logs), global_step=test_best_epoch)



    # Testing with only class layer 0 (BG)

    loss = smp.utils.losses.DiceLoss(ignore_channels=[1])
    metrics = [
        #smp.utils.metrics.IoU(threshold=0.5),
        smp.utils.metrics.IoU(threshold=0.5, ignore_channels=[1]),
    ]

    test_epoch = smp.utils.train.ValidEpoch(
        model=best_model,
        loss=loss,
        metrics=metrics,
        device=DEVICE,
    )

    logs = test_epoch.run(test_dataloader)
    print("logs=", str(logs))
    writer.add_text(f"{opt.exp_name}-test-score-ignore-channel-1", str(logs), global_step=test_best_epoch)



def check_val_full_score(opt):

    # changing test data files into val data

    #opt.test_CSVs = opt.val_CSVs

    opt.record_name = "VAL"

    checkpoint_dict = torch.load(os.path.join(CHECKPOINT_DIR, opt.best_checkpoint_name))

    test_best_epoch =  checkpoint_dict["epoch"]
    best_model = checkpoint_dict["model"]

    print("Model best epoch:", test_best_epoch)
    
    

    preprocessing_fn = smp.encoders.get_preprocessing_fn(opt.encoder, opt.encoder_weights)
    test_dataset = prepare_test_data(opt, preprocessing_fn=None)
    
    test_dataloader = DataLoader(test_dataset, num_workers=12)

    loss = smp.utils.losses.DiceLoss()
    # Testing with two class layers
    metrics = [
        #smp.utils.metrics.IoU(threshold=0.5),
        smp.utils.metrics.IoU(threshold=0.5, ignore_channels=None),
        smp.utils.metrics.Fscore(threshold=0.5, ignore_channels=None),
        smp.utils.metrics.Accuracy(threshold=0.5, ignore_channels=None),
        smp.utils.metrics.Recall(threshold=0.5, ignore_channels=None),
        smp.utils.metrics.Precision(threshold=0.5, ignore_channels=None),
    ]

    test_epoch = smp.utils.train.ValidEpoch(
        model=best_model,
        loss=loss,
        metrics=metrics,
        device=DEVICE,
    )

    logs = test_epoch.run(test_dataloader)
    print("logs=", str(logs))
    writer.add_text(f"{opt.exp_name}-scores-->{opt.record_name}", str(logs), global_step=test_best_epoch)

    # Testing with only class layer 1 (polyps)
    loss = smp.utils.losses.DiceLoss(ignore_channels=[0])
    
    metrics = [
        #smp.utils.metrics.IoU(threshold=0.5),
        smp.utils.metrics.IoU(threshold=0.5, ignore_channels=[0]),
        smp.utils.metrics.Fscore(threshold=0.5, ignore_channels=[0]),
        smp.utils.metrics.Accuracy(threshold=0.5, ignore_channels=[0]),
        smp.utils.metrics.Recall(threshold=0.5, ignore_channels=[0]),
        smp.utils.metrics.Precision(threshold=0.5, ignore_channels=[0]),
    ]

    test_epoch = smp.utils.train.ValidEpoch(
        model=best_model,
        loss=loss,
        metrics=metrics,
        device=DEVICE,
    )

    logs = test_epoch.run(test_dataloader)
    print("logs=", str(logs))
    writer.add_text(f"{opt.exp_name}-val-scores-ignore-channel-0-->{opt.record_name}", str(logs), global_step=test_best_epoch)



    # Testing with only class layer 0 (BG)

    loss = smp.utils.losses.DiceLoss(ignore_channels=[1])
    metrics = [
        #smp.utils.metrics.IoU(threshold=0.5),
        smp.utils.metrics.IoU(threshold=0.5, ignore_channels=[1]),
        smp.utils.metrics.Fscore(threshold=0.5, ignore_channels=[1]),
        smp.utils.metrics.Accuracy(threshold=0.5, ignore_channels=[1]),
        smp.utils.metrics.Recall(threshold=0.5, ignore_channels=[1]),
        smp.utils.metrics.Precision(threshold=0.5, ignore_channels=[1]),
    ]

    test_epoch = smp.utils.train.ValidEpoch(
        model=best_model,
        loss=loss,
        metrics=metrics,
        device=DEVICE,
    )

    logs = test_epoch.run(test_dataloader)
    print("logs=", str(logs))
    writer.add_text(f"{opt.exp_name}-val-scores-ignore-channel-1-->{opt.record_name}", str(logs), global_step=test_best_epoch) 





if __name__ == "__main__":

    #data_loaders = prepare_data()
    print(vars(opt))
    print("Test OK")

    # Train or retrain or inference
    if opt.action == "train":
        print("Training process is strted..!")
        run_train(opt)
        pass

    elif opt.action == "retrain":
        print("Retrainning process is strted..!")
        run_retrain(opt)
        pass

    elif opt.action == "test":
        print("Inference process is strted..!")
        do_test(opt)
        print("Done")

    elif opt.action == "check":
        check_test_score(opt)
        print("Check pass")

    elif opt.action == "check_val":
        check_val_full_score(opt)

    # Finish tensorboard writer
    writer.close()

