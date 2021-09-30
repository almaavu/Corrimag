from sys import argv
from pathlib import Path
import time
import logging

from imageio import imread
from skimage import img_as_float
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from scipy.ndimage.filters import gaussian_filter



CFG = {
            'blur_sigma': 2,
            'in_file_mask':'*.jpg',
            'excluded' : ("VIS", "Video 1", "mosaic", "parameters", "p", "Rh", "Rh-KA1", "Rh-LA1", "U"),
        }


def corrdot(*args, **kwargs):
    corr_r = args[0].corr(args[1], 'pearson')
    corr_text = f"{corr_r:2.2f}".replace("0.", ".")
    ax = plt.gca()
    ax.set_axis_off()
    marker_size = abs(corr_r) * 10000
    ax.scatter([.5], [.5], marker_size, [corr_r], alpha=0.6, cmap="coolwarm",
               vmin=-1, vmax=1, transform=ax.transAxes)
    font_size = abs(corr_r) * 40 + 5
    ax.annotate(corr_text, [.5, .5,],  xycoords="axes fraction",
                ha='center', va='center', fontsize=font_size)

def load_image(fp):
    ''' load image from fp and return numpy float array (0..1) '''
    fp = Path(fp)
    if fp.suffix == ".txt":
        im = np.loadtxt(fp, dtype=np.uint16, delimiter=";")
    else:
        im = imread(fp)
    return img_as_float(im)


def image_array(fpath, blur_sigma=0):
    '''Load and preprocess image as numpy array, cache images for fast reuse.'''
    
    im = load_image(fpath)
    
    if im.ndim > 2: # if RGB or RGBA, use only first channel
        im = im[:,:,0]
        
    im =  gaussian_filter(im, blur_sigma)

    return im


def main():
    
    start_time = time.time() 
    
    # get root dir from command line or use default
    root = argv[1] if len(argv) > 1 else "sample"
    
    # get all files in root dir
    root = Path(root)
    fs = sorted(list(root.glob(CFG["in_file_mask"])))
    fs = [f for f in fs if f.stem not in CFG["excluded"]]
    print("load data")
    data = {f.stem : image_array(f, blur_sigma=2).ravel() for f in fs}
    df = pd.DataFrame(data)


    sns.set(style='white', font_scale=1.6)
    print("pairgrid")
    g = sns.PairGrid(df, aspect=1, diag_sharey=False)
    print("lower")
    g.map_lower(sns.scatterplot)
    print("diag")
    g.map_diag(sns.histplot, kde_kws={'color': 'black'})
    print("upper")
    g.map_upper(corrdot)
    g.set(yticks=[])
    g.set(xticks=[])
    logging.info(f"Done in {time.time()-start_time:.2f} s")

main()