import logika_igre

import logging
import random

globina = 2

NEODLOCENO = logika_igre.NEODLOCENO
NI_KONEC = logika_igre.NI_KONEC

# Vrednosti igre
ZMAGA = 10**9
NESKONCNO = 100 * ZMAGA

class Alfabeta():

    def __init__(self, globina):
        self.globina = globina  # do katere globine iščemo?
        self.prekinitev = False # ali moramo končati?
        self.igra = None # objekt, ki opisuje igro (ga dobimo kasneje)
        self.jaz = None  # katerega igralca igramo (podatek dobimo kasneje)
        self.poteza = None # sem napišemo potezo, ko jo najdemo

    def prekini(self):
        """Metoda, ki jo pokliče GUI, če je treba nehati razmišljati, ker
           je uporabnik zaprl okno ali izbral novo igro."""
        self.prekinitev = True

    def stevilo_polj_v_vzorcu(self, vzorec, barva):
        '''Vrne število polj izbrane barve v izbranem vzorcu'''
        stevilo_polj = 0
        for (i, j) in vzorec:
            if self.igra.igralno_polje[i][j] == barva:
                stevilo_polj += 1
            elif self.igra.igralno_polje[i][j] == logika_igre.nasprotnik(barva):
                return 0
        return stevilo_polj

    def vrednost_pozicije(self):
        '''Smo v trenutnem stanju, torej sestkotniki so obarvani, kot pac so.
        Gremo po vseh poljih in za vsako polje pogledamo, koliko lahko doprinese
        k vrednosti trenutne pozicije za dolocenega igralca. Ce v nekem vzorcu nastopa
        vsaj eno polje nasprotnikove barve, to polje ne doprinese nicesar, sicer pa doloceno vrednost.'''
        vrednosti = {
            (6,0) : ZMAGA,
            (0,6) : -ZMAGA,
            (5,0) : ZMAGA//10,
            (0,5) : -ZMAGA//10,
            (4,0) : ZMAGA//100,
            (0,4) : -ZMAGA//100,
            (3,0) : ZMAGA//50000,
            (0,3) : -ZMAGA//50000,
            (2,0) : ZMAGA//5000000,
            (0,2) : -ZMAGA//5000000,
            (1,0) : 1,
            (0,1) : -1,
            (0,0) : 0
            }
        vr_pozicije = 0

        for i in range(logika_igre.velikost_matrike): # vrstica
            for j in range(logika_igre.velikost_matrike): # stolpec
                vzorci = self.igra.zmagovalni_vzorci(i, j) 
                for vzorec in vzorci:
                    # pogledamo število lastnih polj v vzorcu, nato pa še število polj nasprotnika
                    x1 = self.stevilo_polj_v_vzorcu(vzorci[vzorec], self.igra.na_potezi)
                    x2 = self.stevilo_polj_v_vzorcu(vzorci[vzorec], logika_igre.nasprotnik(self.igra.na_potezi))
                    vr_pozicije += vrednosti[(x1,x2)]
        return vr_pozicije

    def izracunaj_potezo(self, igra):
        self.igra = igra
        self.prekinitev = False # Glavno vlakno bo to nastavilo na True, če moramo nehati
        self.jaz = self.igra.na_potezi
        self.poteza = None # Sem napišemo potezo, ko jo najdemo
        # Poženemo alfabeta
        (poteza, vrednost) = self.alfabeta(self.globina, True)
        self.jaz = None
        self.igra = None
        if self.prekinitev == False:
            # Potezo izvedemo v primeru, da nismo bili prekinjeni
            self.poteza = poteza

    def alfabeta(self, globina, maksimiziramo, alfa=-NESKONCNO, beta=NESKONCNO):
        '''vrne (poteza, vrednost)'''
        
        if self.prekinitev == True:
            # Sporočili so nam, da moramo prekiniti
            return (None, 0)
       
        # pogledamo kakšno je trenutno stanje igre
        (zmagovalec, zmagovalna_polja) = self.igra.stanje_igre()

        if zmagovalec in (logika_igre.prvi, logika_igre.drugi, NEODLOCENO):
            # Igre je konec, vrnemo njeno vrednost
            if zmagovalec == self.jaz:
                return (None, ZMAGA)
            elif zmagovalec == logika_igre.nasprotnik(self.jaz):
                return (None, -ZMAGA)
            else:
                return (None, 0)

        elif zmagovalec == NI_KONEC:
            # Igre ni konec
            
            # prispeli smo do željene globine, pogledamo vrednost igre
            if globina == 0:
                return (None, self.vrednost_pozicije())
            
            # nismo na željeni globini, naredimo še eno stopnjo alfabeta
            if maksimiziramo:
                najboljse_poteze = []
                vrednost = -NESKONCNO
                poteza = None
                for (i,j) in self.igra.veljavne_poteze():
                    self.igra.izvedi_potezo(i, j)
                    pomozna_vr = self.alfabeta(globina-1, not maksimiziramo, alfa, beta)[1]
                    self.igra.razveljavi()
                    
                    if pomozna_vr > vrednost:
                        najboljse_poteze = [(i, j)]
                        vrednost = pomozna_vr
                    elif pomozna_vr == vrednost:
                        najboljse_poteze.append((i, j))
                        vrednost = pomozna_vr

                    alfa = max(alfa, vrednost)
                    if beta < alfa:
                        break

                poteza = random.choice(najboljse_poteze)
                assert (poteza is not None), "alfabeta: izračunana poteza je None"
                return (poteza, vrednost)
            
            # minimiziramo
            else:
                najboljse_poteze = []
                vrednost = NESKONCNO
                poteza = None
                for (i,j) in self.igra.veljavne_poteze():
                    self.igra.izvedi_potezo(i, j)
                    pomozna_vr = self.alfabeta(globina-1, not maksimiziramo, alfa, beta)[1]
                    self.igra.razveljavi()
                    
                    if pomozna_vr < vrednost:
                        najboljse_poteze = [(i, j)]
                        vrednost = pomozna_vr
                    elif pomozna_vr == vrednost:
                        najboljse_poteze.append((i, j))
                        vrednost = pomozna_vr

                    beta = min(beta, vrednost)
                    if beta < alfa:
                        break

                poteza = random.choice(najboljse_poteze)
                assert (poteza is not None), "alfabeta: izračunana poteza je None"
                return (poteza, vrednost)

        else:
            assert False, "alfabeta: nedefinirano stanje igre"

