import threading  # za vzporedno izvajanje
import logging

from alfabeta import *

######################################################################
## Igralec računalnik

class Racunalnik():
    def __init__(self, gui, algoritem):
        self.gui = gui
        self.algoritem = algoritem # Algoritem, ki izračuna potezo
        self.mislec = None # Vlakno (thread), ki razmišlja

    def igraj(self):
        """Igraj potezo, ki jo vrne algoritem."""

        # Naredimo vlakno, ki mu podamo *kopijo* igre (da ne bo zmedel GUIja):
        self.mislec = threading.Thread(
            target=lambda: self.algoritem.izracunaj_potezo(self.gui.igra.kopija()))

        # Poženemo vlakno:
        self.mislec.start()

        # Gremo preverjat, ali je bila najdena poteza:
        self.gui.plosca.after(100, self.preveri_potezo)

    def preveri_potezo(self):
        """Vsakih 100ms preveri, ali je algoritem že izračunal potezo."""
        poteza = self.algoritem.poteza
        if  poteza != None:         
            # self.algoritem.poteza vrne par (i, j) funkcija povleci_potezo 
            # pa sprejme i, j, zato uporabimo *poteza
            self.gui.povleci_potezo(*poteza)
            
            # Vzporedno vlakno ni več aktivno, zato ga "pozabimo"
            self.mislec = None
        
        else:
            # Algoritem še ni našel poteze, preveri še enkrat čez 100ms
            self.gui.plosca.after(100, self.preveri_potezo)

    def prekini(self):
        '''prekine razmišljanje računalnika'''
        # To metodo kliče GUI, če je treba prekiniti razmišljanje.
        if self.mislec:
            # Algoritmu sporočimo, da mora nehati z razmišljanjem
            self.algoritem.prekini()
            # Počakamo, da se vlakno ustavi
            self.mislec.join()
            self.mislec = None

    def klik(self, i, j):
        '''se odzove na klik uporabnika, ko je na potezi računalnik'''
        # Računalnik ignorira klike uporabnika
        pass
