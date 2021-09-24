# correlate-element-maps
https://github.com/almaavu/correlate-element-maps

**Korelace MA-XRF or SEM-EDS prvkových map.** 
 Výpočet Personova korelačního koeficientu dvojic map, uložení tabulky s výsledky do XLS souboru. 

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




### TODO:
-



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
