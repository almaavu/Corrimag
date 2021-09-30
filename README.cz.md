# correlate-element-maps
https://github.com/almaavu/correlate-element-maps

**Korelace MA-XRF or SEM-EDS prvkových map.** 
 Výpočet Personova korelačního koeficientu dvojic map, uložení tabulky s výsledky do XLS souboru. 


### Instalace:
Instalace programovacího jazyka Python3

    https://www.python.org/downloads/
    
Instalace programu correlate-element-maps

    python -m pip install git+https://github.com/almaavu/correlate-element-maps.git

### Použití:

    python -m correlate_element_maps --maps-dir="d:/maps"
    
Skript je možné spustit i bez instalace:

    python correlate_element_maps.py --maps-dir="d:/maps"


### Vstup: 
- Cesta a názvy souborů prvkových map.
- Tabulka vybraných dvojic prvků určených pro výpočet korelace. (Alternativně lze korelace počítat pro všechny možné kombinace prvkových map, pokud je přijatelná delší doba potřebná pro výpočet.) 


### Zpracování:
- Načtení dvojic prvkových map. Obrázky se načítají do cache pro urychlení zpracování stejného obrázku v dalších krocích.
- Výpočet Pearsonova korelačního koeficientu.
- Zpracování výsledků ve formátu pandas DataFrame, řazení podle hodnoty r<sup>2</sup>.
- Uložení do XLS souboru.


### Výstup:
- XLS soubor s výsledky.



### Odkazy:

https://en.wikipedia.org/wiki/Pearson_correlation_coefficient

https://imagej.net/imaging/colocalization-analysis




## Ukázka:

### Prvkové mapy:
<p align="center">

</p>

### Výsledek:
<p align="center">

</p>

<p align="center">
  <img src="sample/Ca.jpg" width="100" title="">
  <img src="sample/Cr.jpg" width="100" title="">
<img src="sample/Hg.jpg" width="100" title="">
<img src="sample/Pb-LB.jpg" width="100" title="">
<img src="sample/S.jpg" width="100" title="">
<img src="sample/Zn-KB.jpg" width="100" title="">
</p>

### Result:
<p align="center">
  <img src="samples/false_color_images/ir_image_vis_image_falsecolor.png" width="150">
</p>
