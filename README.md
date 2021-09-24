# falsevisir
https://github.com/almaavu/falsevisir

**Combine infrared and visible light images of the same object to false colors automatically.**

### Input: 
file paths of visible light image (RGB) and infrared image (RGB or grey)



### Process:
- resize images to same height
- warp images to fit when overlayed (images must have similar features, otherwise it may fail)
- combine images to false colors - R channel from IR image, 
    G channel from VIS-R and B channel from VIS-G (VIS-B is discarded)
- blend images (50 % IR, 50 % VIS)




### Output:
- False color image
- Blend image
- VIS image resized and warped
- IR image resized and warped




### TODO:
- remove first resize step? 



### resources:

https://en.wikipedia.org/wiki/False_color

https://chsopensource.org/infrared-false-color-photography-irfc/

https://en.wikipedia.org/wiki/Affine_transformation


## Example:

### Source images:
<p align="center">
  <img src="samples/vis_image.jpg" width="150" title="">
  <img src="samples/ir_image.jpg" width="150" alt="">
</p>

### Result:
<p align="center">
  <img src="samples/false_color_images/ir_image_vis_image_falsecolor.png" width="150">
</p>
