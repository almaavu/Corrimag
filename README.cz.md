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

<p align="center">
  <img src="sample/Ca.jpg" width="100" title="">
  <img src="sample/Cr.jpg" width="100" title="">
<img src="sample/Hg.jpg" width="100" title="">
<img src="sample/Pb-LB.jpg" width="100" title="">
<img src="sample/S.jpg" width="100" title="">
<img src="sample/Zn-KB.jpg" width="100" title="">
</p>

### Výsledek:
<table border="1" style="margin:auto">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>pair</th>
      <th>r2</th>
      <th>r</th>
      <th>m</th>
      <th>b</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1</th>
      <td>Ca Hg</td>
      <td>0.80</td>
      <td>0.90</td>
      <td>0.35</td>
      <td>0.03</td>
    </tr>
    <tr>
      <th>10</th>
      <td>Hg S</td>
      <td>0.45</td>
      <td>0.67</td>
      <td>0.98</td>
      <td>-0.26</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Ca S</td>
      <td>0.21</td>
      <td>0.45</td>
      <td>0.26</td>
      <td>-0.02</td>
    </tr>
    <tr>
      <th>0</th>
      <td>Ca Cr</td>
      <td>0.03</td>
      <td>0.16</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <th>6</th>
      <td>Cr Pb-LB</td>
      <td>0.01</td>
      <td>0.11</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <th>2</th>
      <td>Ca Pb-LB</td>
      <td>0.00</td>
      <td>0.06</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <th>5</th>
      <td>Cr Hg</td>
      <td>0.00</td>
      <td>0.05</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <th>8</th>
      <td>Cr Zn-KB</td>
      <td>0.00</td>
      <td>0.03</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <th>7</th>
      <td>Cr S</td>
      <td>0.00</td>
      <td>0.01</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <th>13</th>
      <td>Pb-LB Zn-KB</td>
      <td>0.00</td>
      <td>0.00</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <th>4</th>
      <td>Ca Zn-KB</td>
      <td>0.00</td>
      <td>-0.06</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <th>12</th>
      <td>Pb-LB S</td>
      <td>0.00</td>
      <td>-0.07</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <th>9</th>
      <td>Hg Pb-LB</td>
      <td>0.00</td>
      <td>-0.07</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <th>11</th>
      <td>Hg Zn-KB</td>
      <td>0.09</td>
      <td>-0.30</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <th>14</th>
      <td>S Zn-KB</td>
      <td>0.67</td>
      <td>-0.82</td>
      <td>-0.55</td>
      <td>0.54</td>
    </tr>
  </tbody>
</table>
