#!/usr/bin/env python3
'''
Calculate Pearson correlation for image pairs from given folder -> dataframe
- all images must be of same shape
- image preprocessing: oval mask for miniature paintings, gaussian blur)
- sort and filter results by r value 
- save results to XLSX file

r = Pearson correlation coefficient
r2 = Coefficient of determination
m = regression slope
a = regression intercept

sources:
https://en.wikipedia.org/wiki/Pearson_correlation_coefficient
https://en.wikipedia.org/wiki/Coefficient_of_determination
https://en.wikipedia.org/wiki/Simple_linear_regression
https://en.wikipedia.org/wiki/Colocalization



TODO:
    - correlation matrix with histograms
    https://stackoverflow.com/questions/48139899/correlation-matrix-plot-with-coefficients-on-one-side-scatterplots-on-another
'''

# IMPORTS --------------------------------------------



from sys import argv
import logging
import time
from pathlib import Path
import copy
import itertools
from functools import lru_cache

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import rcParams, cm
from matplotlib.colors import LogNorm
from scipy.ndimage.filters import gaussian_filter
from imageio import imread
from skimage import img_as_float

from pyalma.common.almalib import load_image
from pyalma.ma_xrf.maps.tools import im_mask

SC_FPATH = Path(__file__).resolve()
COMMENTS_FPATH = SC_FPATH.parent / "correlations_comments.xlsx"


CFG = {
            'oval_mask': False,
            'blur_sigma': 2,
            'min_threshold': 0.1,
            'max_threshold': .95,
            'view_gamma': .6,
            'min_r2': .1,
            'in_file_mask':'*.jpg',
            'in_file_bitdepth':16,
            'excluded' : ("VIS", "Video 1", "mosaic", "parameters", "p", "Rh", "Rh-KA1", "Rh-LA1", "U"),
        }


pd.options.display.float_format = '{:,.2f}'.format
plt.style.use('dark_background')
rcParams['figure.figsize'] = 3, 3
rcParams['pdf.fonttype'] = 42
rcParams['ps.fonttype'] = 42
rcParams['font.size'] = 12
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
    
    

    logging.info(f"{__file__} started")

    # get root dir from command line or use default
    root = argv[1] if len(argv) > 1 else "sample"
    
    # get all files in root dir
    root = Path(root)
    fs = sorted(list(root.glob(CFG["in_file_mask"])))
    fs = [f for f in fs if f.stem not in CFG["excluded"]]
    
    # get all paths combinations
    pairs = list(itertools.combinations(fs, 2))
    # print(pairs)

    c = Correlations(pairs, cfg=CFG)
    print(c.result.fillna(''))

    c.to_excel(root / "correlations.xlsx")
    c.result.fillna('').to_html(Path("sample") / "correlations.html")
    
    c.plot_2D_hist(outdir="2d_hist")
    
    logging.info(f"Correlation done in {time.time()-start_time:.2f} s")


#%%
class Correlations:
    """Calculate correlations ."""

    def __init__(self, pairs, cfg):
        self.cfg = cfg
        self.path_pairs = pairs

        self.name_pairs = [f"{f1.stem} {f2.stem}" for f1,f2 in self.path_pairs] # all name combinations
        
        self.array_pairs = self._load_arrays()  # list of numpy array pairs
        self.result = self.multiprocess_correlations(self.array_pairs)

    def _load_arrays(self):
        '''Load images from files, preprocess images (smoothing, oval mask)
        Return: list of numpy array pairs
        '''
        rows = []
        for pair in self.path_pairs:
            images = [cached_array(f) for f in pair]
            rows.append(images)
        return rows

    def _list2df(self, results):
        df = pd.DataFrame(results)
        df = df.astype(float)
        df.insert(0, 'pair', self.name_pairs)
        df.sort_values('r', inplace=True, ascending=False)
        return df

    def process_correlations(self, array_pairs):
        results = []
        for x,y in array_pairs:
            c = pearson_correlation(x,y)
            results.append(c)

        return self._list2df(results)

    def multiprocess_correlations(self, array_pairs):
        '''about 30% faster than single process, can be optimized better?'''
        from multiprocessing import Pool

        with Pool() as pool:
            results = pool.starmap(pearson_correlation, (array_pairs))
        
        return self._list2df(results)


    def add_comments(self):
        comments = pd.read_excel(COMMENTS_FPATH, index_col=0)
        df = self.result.merge(comments, left_on='pair', right_index=True)
        return df

    def plot_2D_hist(self, outdir="2d_hist"):
        outdir = Path(outdir)
        outdir.mkdir(exist_ok=True)
        
        for pair in self.path_pairs:
            a, b = pair
            plot_2d_hist(cached_array(a), cached_array(b), a.stem, b.stem, fpath=outdir / f"{a.stem}_{b.stem}")
        
        
        
        
    def to_excel(self, fpath):
        
        df = self.result
        sheet = "correlations"
        with pd.ExcelWriter(fpath, engine='xlsxwriter') as writer:

            df.to_excel(writer, index=False, sheet_name=sheet, freeze_panes=(1,1), float_format="%.2f")

            worksheet = writer.sheets[sheet]
            worksheet.set_column(0, 0, 20)  # first column width
            worksheet.set_column(1, 20, 10)  # next col widths
            worksheet.conditional_format('B1:B500', {'type': '3_color_scale',
                                                 'min_type':'num', 'min_value':.4,'min_color': "#ffffff",
                                                'mid_type':'num', 'mid_value':.9, 'mid_color': "#ffff99",
                                                'max_type':'num', 'max_value':1, 'max_color': "#ff9999"})
            # ~ writer.save()






#%%
# FUNCTIONS --------------------------------------------

# alternative to ImageCache

@lru_cache()
def cached_array(fpath, blur_sigma=0, oval_mask=False):
    '''Load and preprocess image as numpy array, cache images for fast reuse.'''
    
    im = load_image(fpath)
    if im.ndim > 2: # if RGB or RGBA, use only first channel
        im = im[:,:,0]
    im =  blur(im, blur_sigma)
    if oval_mask:
        im = im_mask.apply_oval_mask(im)
    # print(im.shape, im.dtype, type(im))
    #im = im.ravel()
    return im


def load_image(fp):
    ''' load image from fp and return numpy float array (0..1) '''
    fp = Path(fp)
    if fp.suffix == ".txt":
        im = np.loadtxt(fp, dtype=np.uint16, delimiter=";")
    else:
        im = imread(fp)
    return img_as_float(im)


def blur(array, sigma):
    return gaussian_filter(array, sigma)


def pearson_correlation(x, y):
    """
    Args: x,y - masked arrays
    Return: dict of floats
    
    """
    x, y = x.ravel(), y.ravel()
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



def dataframe_from_nested_dict(list_of_dicts):
    '''Pandas wants the MultiIndex values as tuples, not nested dicts.
    Convert your dictionary to the right format before you pass it to DataFrame'''
    new_list = []
    for d in list_of_dicts:
        row = {(outerKey, innerKey): values for outerKey, innerDict in d.items() for innerKey, values in innerDict.items()}
        new_list.append(row)
    df = pd.DataFrame(new_list)
    return(df)

def plot_2d_hist(y, x, ylab, xlab, fpath=None, bns=50, norm=LogNorm()):
    """
    https://foxlab.ucdavis.edu/2013/06/05/visualizing-the-correlation-of-two-volumes/
    """
    fpath = fpath or f"{ylab}_{xlab}_hist.png"
    plt.rcParams.update({'font.size':32})
    from matplotlib.ticker import NullFormatter
    logging.info(f"plot 2D histogram of {xlab}, {ylab}")
    x, y = x.ravel(), y.ravel()
    
    fig = plt.figure(2, figsize=(8, 8)) # fig number 2
    

    axHist2d = plt.subplot2grid( (9,9), (0,0), colspan=9, rowspan=9)
    H, xedges, yedges = np.histogram2d( x, y, bins=bns )
    axHist2d.imshow(H.T + .001, interpolation='nearest', aspect='auto', cmap='jet',  norm=norm)
    
    # mpl.rc('xtick', labelsize=15) 
    # mpl.rc('ytick', labelsize=15) 
    axHist2d.set_xlabel(xlab, fontsize=20)
    axHist2d.set_ylabel(ylab, fontsize=20)

    nullfmt = NullFormatter()

    axHist2d.invert_yaxis()
#    axHist2d.autoscale()

#    print(x,y,x.min, )
    # xmin = max(x.max(),50)
    # ymin = max(y.max(),50)

    # axHist2d.set_xlim( [0,xmin] )
    # axHist2d.set_ylim( [0,ymin] )
    
    plt.tick_params(
                    axis='both',          # changes apply to the x-axis
                    which='both',      # both major and minor ticks are affected
                    left=False,      # ticks along the bottom edge are off
                    right=False,      # ticks along the bottom edge are off
                    bottom=False,      # ticks along the bottom edge are off
                    top=False,         # ticks along the top edge are off
                    labelbottom=False,
                    labelleft=False,
                    )
    
    
    
    
    
    # save to file
    
    
    
    
    fname = f"{ylab}_{xlab}.png"
#    print(f"save {fname}")
    plt.tight_layout()
    fig.savefig(fpath)
    plt.show()
    plt.clf()


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










# %%

INTERSECT_CMAP = set_nan_color('black') # not working why?

if __name__ == "__main__":
    main()
