#!/usr/bin/env python3
'''
Calculate Pearson correlation for each image in given folder -> dataframe
- image preprocessing: oval mask for miniature paintings, gaussian blur)
- sort and filter results by minimal r2 value (set in CFG)
- add comments from file correlations_comments.xls
Save results to XLSX
'''

# IMPORTS --------------------------------------------

import numpy as np

from sys import argv
import logging
import time
from pathlib import Path
import copy
import itertools
from functools import lru_cache
#from imageio import imread

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams, cm
from matplotlib.colors import LogNorm

from qq.npimage import blur
from pyalma.common.almalib import load_image
from pyalma.ma_xrf.maps.tools import im_mask

SC_FPATH = Path(__file__).resolve()
COMMENTS_FPATH = SC_FPATH.parent / "correlations_comments.xlsx"


CFG = {
            'oval_mask': True,
            'blur_sigma': 3,
            'blur_mode': 'gaussian',
            'min_threshold': 0.1,
            'max_threshold': .95,
            'view_gamma': .6,
            'min_r2': .1,
            'in_file_extension':'.png',
            'in_file_bitdepth':16,
            'excluded' : ("VIS", "Video 1", "mosaic", "parameters", "p", "Rh", "Rh-KA1", "Rh-LA1", "U"),
        }


plt.style.use('dark_background')
rcParams['figure.figsize'] = 3, 3
rcParams['pdf.fonttype'] = 42
rcParams['ps.fonttype'] = 42
rcParams['text.usetex'] = False
rcParams['font.sans-serif'] = 'Arial'
rcParams['font.family'] = 'sans-serif'
BG_COLOR = (.2,.2,.2)
rcParams['axes.facecolor'] = BG_COLOR
rcParams['figure.facecolor'] = BG_COLOR
rcParams['savefig.facecolor'] = BG_COLOR
plt.set_cmap("jet")
HIST_CMAP = copy.copy(cm.get_cmap()).set_bad('black')


PLOT_SIZE = 5
DPI = 240


# disable debug logging
pil_logger = logging.getLogger('PIL')
pil_logger.setLevel(logging.INFO)
logging.getLogger('matplotlib.font_manager').disabled = True


# %%



def main():

    start_time = time.time()

    logging.basicConfig(
        level=20,
        format='!%(levelno)s [%(module)10s%(lineno)4d]\t%(message)s')

    root = argv[1] if len(argv) > 1 else "."

    correlate_images(root)

    print(f"Correlation done in {time.time()-start_time:.2f} s")



def correlate_images(root="."):

    # Get filepaths
    root = Path(root).resolve()
    absdir = Path(root, "maps_abs").resolve()

    print(f"Correlate files in {absdir}")
    fs = sorted(list(absdir.glob("*"+CFG["in_file_extension"])))
    fs = [f for f in fs if f.stem not in CFG['excluded']]
    [print(f.stem,end=" ") for f in fs]
    print()

    # Calculate correlations of all maps in directory
    c = Correlations(fs, cfg=CFG)
    
    # add comments from xls file
    c.add_comments() 
        
    print(c.result)

    # Save results to XLS
    c.save(root / f"{get_meas_id(root)}_correlations.xls")

#%%
# FUNCTIONS --------------------------------------------


def pearson_correlation(x, y):
    """
    Args: x,y - 1d masked arrays
    Return: dict of floats
    """
    r = np.ma.corrcoef(x, y)[0, 1]
    r2 = r**2
    coef = (np.nan, np.nan)
    if r2 >= CFG['min_r2']:
        try:
            coef = np.ma.polyfit(y, x, deg=1)   # y,x => ratio el1 / el2
        except BaseException:
            logging.exception("Polyfit failed")
    return {"r2":r2, "r":r, "m":coef[0], "b":coef[1]}

def thresholded_pearson_correlation(x, y, tmin, tmax):
    """
    Mask data where data <= or >= than thresholds,
    get pearson correlations.
    """
    x = np.ma.masked_where((x <= tmin) | (x >= tmax), x, copy=True)
    y = np.ma.masked_where((y <= tmin) | (y >= tmax), y, copy=True)
    return pearson_correlation(x, y)



def get_meas_id(root):
    '''Get measurement id from parent folder name'''
    return Path(root).stem.split("_")[0]



def dataframe_from_nested_dict(list_of_dicts):
    '''Pandas wants the MultiIndex values as tuples, not nested dicts.
    Convert your dictionary to the right format before you pass it to DataFrame'''
    new_list = []
    for d in list_of_dicts:
        row = {(outerKey, innerKey): values for outerKey, innerDict in d.items() for innerKey, values in innerDict.items()}
        new_list.append(row)
    df = pd.DataFrame(new_list)
    return(df)

def plot_2d_hist(y, x, ylab, xlab, outdir=".", bns=range(0,5000,1), ylim=50, norm=LogNorm()):
    """
    https://foxlab.ucdavis.edu/2013/06/05/visualizing-the-correlation-of-two-volumes/
    """
    print("x,y,x.min,y.min, x.max, y.max")
    print(x,y,x.min(),y.min(), x.max(), y.max())
    plt.rcParams.update({'font.size':32})
    from matplotlib.ticker import NullFormatter
    logging.debug(f"plot hist {xlab} {ylab} {x.shape} {y.shape}")
    fig = plt.figure(2, figsize=(8, 8)) # fig number 2

    axHist2d = plt.subplot2grid( (9,9), (0,0), colspan=9, rowspan=9)

    H, xedges, yedges = np.histogram2d( x, y, bins=(bns,bns) )
    axHist2d.imshow(H.T + .001, interpolation='nearest', aspect='auto', cmap='jet',  norm=norm)

    axHist2d.set_xlabel(xlab, fontsize=32)
    axHist2d.set_ylabel(ylab, fontsize=32)

    nullfmt = NullFormatter()

    axHist2d.invert_yaxis()
#    axHist2d.autoscale()

#    print(x,y,x.min, )
    xmin = max(x.max(),50)
    ymin = max(y.max(),50)

    axHist2d.set_xlim( [0,xmin] )
    axHist2d.set_ylim( [0,ymin] )
    # save to file
    fname = f"{ylab}_{xlab}.png"
#    print(f"save {fname}")
    plt.tight_layout()
    fig.savefig(outdir / fname)
    fig.clear()


def set_nan_color(col='white'):
    import copy
    cmap = cm.get_cmap()
    my_cmap = copy.copy(cmap)
    my_cmap.set_bad(color=col)
    return my_cmap


def get_unique_items(nested_iterable):
    import itertools
    return list(itertools.chain.from_iterable(nested_iterable))


#    plot_stats(result, images)
def im_intensity(rgb_arr):
    ''' get mean of rgb values -> grey image '''
    if rgb_arr.ndim == 2:
        return rgb_arr
    return np.mean(rgb_arr, axis=2)

def apply_gamma_255(y):
    y = 255 * (y / 255) ** float(CFG['view_gamma'])
    return y.astype(np.uint8)

def plot_stats(result, images):
    # Add a table at the bottom of the axes
    # means = [round(np.nanmean(y),2) for y in im_list]
    # std_devs = [round(np.nanstd(y),2) for y in im_list]
#    print(images)
#    print(result.elements)
    name1, name2 = result.elements
#    print(name1, images[name1])
    data = [
        [images[name1].mean(), images[name2].mean()],
        [images[name1].std(), images[name2].std()],
        ["", ""],
        [result.r, result.r2],
        [result.coef[0], result.coef[1]],
    ]

    data2 = []
    for row in data:
        row2 = []
        for cell in row:
            if isinstance(cell, float):
                row2.append(round(cell, 2))
            else:
                row2.append(cell)
        data2.append(row2)

#    print(data2)

    ncols = 3
    table = {
        #        'colWidths' :   [.05,.05],
        'cellLoc': 'center',
        'rowLoc': 'center',
        'colLabels': result.elements,
        'rowLabels': [r'$\bar{x}$', "σ", "", "r, $r^2$", "m, b"],
        'cellText': data2,
        'colWidths': [1 / (ncols + 2)] * ncols,    # narrow columns

    }
    stat_table = plt.table(
        **table,
        loc='bottom',
        edges='closed')  # , loc=4 means 'best'

    # adjust table properties
    stat_table.set_fontsize(8)

    for k, cell in stat_table._cells.items():
        cell.set_edgecolor('white')





# alternative to ImageCache

@lru_cache()
def im_array(fpath, blur_sigma=0, blur_mode="gaussian", oval_mask=True):
    im = load_image(fpath)
    im =  blur(im, blur_sigma, blur_mode)
    if oval_mask:
        im = im_mask.apply_oval_mask(im)
    # print(im.shape, im.dtype, type(im))
    #im = im.ravel()
    return im

#%%

class ImageCache:
    '''Load image from cache if cached else from disk.'''

    def __init__(self, cfg):
        self.cached = {}
        self.sigma = cfg['blur_sigma']
        self.mode = cfg['blur_mode']

    def get(self, fpath):

        fpath = Path(fpath)
        if not fpath in self.cached:
            # load numpy array
            im = load_image(fpath)
            # apply noise reduction
            im =  blur(im, self.sigma, self.mode)
            if CFG["oval_mask"]:
                im = im_mask.apply_oval_mask(im)
                # print(im.shape, im.dtype, type(im))
            im = im.ravel()
            # save to cache
            self.cached[fpath] = im

        return self.cached[fpath]



#%%
class Correlations:
    """Calculate correlations ."""

    def __init__(self, fpaths, cfg):
        self.cfg = cfg
        self.fpaths = fpaths
        self.image_cache = ImageCache(cfg) # cache images - faster run
        self.pairs = list(itertools.combinations(self.fpaths, 2)) # all Paths combinations
        self.names = [f"{f1.stem} {f2.stem}" for f1,f2 in self.pairs] # all name combinations
        self.arrays = self._load_arrays()  # all array combinations
        self.result = self.multiprocess_correlations()
#        self.result = self.process_correlations()
        self.result = self.add_comments()

    def _load_arrays(self):
        rows = []
        for pair in self.pairs:
#            print(pair)
            images = [self.image_cache.get(f) for f in pair]
            rows.append(images)
#        print(rows)
        return rows

#    def process_correlations(self):
#        rows = []
#        for x,y in self.arrays:
#            c = pearson_correlation(x,y)
#            rows.append(c)
#
#        df = pd.DataFrame(rows)
#        df = df.astype(float)
#        df.set_index(pd.Series(self.names), inplace=True)
#
#        return df

    def multiprocess_correlations(self):
        '''about 30% faster than single process, can be optimized better?'''
        from multiprocessing import Pool

        with Pool() as pool:
            c = pool.starmap(pearson_correlation, (self.arrays))

        df = pd.DataFrame(c)
        df = df.astype(float)
        df.insert(0, 'pair', self.names)
#        df = df.rename_axis("pair")
        # print(df)
#        df = df.index.names = ['pair']

        return df


    def add_comments(self):
        comments = pd.read_excel(COMMENTS_FPATH, index_col=0)
        df = self.result.merge(comments, left_on='pair', right_index=True)
        return df


    def save(self, fpath):
        
        df = self.result

        # df = df[df.r2 > self.cfg["min_r2"]]

        df = df.sort_values(by='r', ascending=False)

        # print(df)

        df1 = df
        # df1 = df[(~(df.overlap==1) & ~(df.identity==1))]
        df3 = df[(df.overlap==1)]
        df2 = df[(df.identity==1)]
        df4 = df[(df.pigment==1)]

        dfs = {'correlations':df1,'identity':df2,'overlaps':df3, 'pigment':df4}
        sheets = dfs.keys()

        fpath = Path(fpath).with_suffix(".xlsx")

        with pd.ExcelWriter(fpath, engine='xlsxwriter') as writer:

            for sheet in sheets:

                df = dfs[sheet]
                df.to_excel(writer, index=False, sheet_name=sheet, freeze_panes=(1,1),float_format="%.2f")

                worksheet = writer.sheets[sheet]
                worksheet.set_column(0, 0, 20)  # first column width
                worksheet.set_column(1, 20, 10)  # next col widths
                worksheet.conditional_format('B1:B500', {'type': '3_color_scale',
                                                     'min_type':'num', 'min_value':.4,'min_color': "#ffffff",
                                                    'mid_type':'num', 'mid_value':.9, 'mid_color': "#ffff99",
                                                    'max_type':'num', 'max_value':1, 'max_color': "#ff9999"})
                # ~ writer.save()







# %%

INTERSECT_CMAP = set_nan_color('black') # not working why?

if __name__ == "__main__":
    main()
